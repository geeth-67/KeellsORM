import uuid

import psycopg
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession

from models import PendingInsertRequest

load_dotenv()

DB_URL = "postgresql+psycopg2://cclarke:admin@localhost:5432/keells"

db = SQLDatabase.from_uri(DB_URL)

model = ChatOpenAI(model="gpt-3.5-turbo")

toolkit = SQLDatabaseToolkit(db=db , llm=model)

tools = toolkit.get_tools()

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect,
    top_k=5,
)

POSTGRES_CONN = psycopg.connect(
    dbname="keells",
    user="cclarke",
    password="admin",
    host="localhost",
    port="5432",
    autocommit=True
)

checkpointer = PostgresSaver(POSTGRES_CONN)

checkpointer.setup()

sql_agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer
)

async def propose_insert(query : str , session : AsyncSession):
    schema_info = db.get_table_info()
    prompt = f"""
    You are a SQL assistant. Generate exactly one SQL INSERT Statement
    for {db.dialect}. Use the provided schema and do NOT output anything
    except the SQL statement. Do not wrap it in code fences. \n\n
    
    Schema: \n
    {schema_info}\n
    User Required:
    {query}
    
    """

    response = model.invoke([
        SystemMessage(content="You only return a single SQL statement."),
        HumanMessage(content=prompt),
    ])

    sql = response.content if hasattr(response, "content") else str(response)

    approval_id = str(uuid.uuid4())
    pending_request = PendingInsertRequest(
        id=approval_id,
        query=query,
        sql=sql,
        status='pending'
    )

    session.add(pending_request)
    await session.commit()
    return {"approval_id": approval_id, "sql": sql}


async def approve_and_execute(approval_id : str, session : AsyncSession ,approve : bool):
    pending_request = await session.get(PendingInsertRequest,approval_id)

    if not pending_request:
        raise ValueError(f"Approval id {approval_id} does not exist")

    if not approve:
        pending_request.status = "rejected"
        await session.commit()
        return "Rejected"

    sql = pending_request.sql
    result = db.run(sql)
    pending_request.status = "approved"
    await session.commit()
    return str(result)


def query_db_with_natural_language(query : str , thread_id : str = "1"):

    try:
        config = {"configurable" : {"thread_id" : thread_id}}
        result = None

        for step in sql_agent.stream(
                {"messages" : [{"role" : "user" , "content" : query}]},
                config,
            stream_mode="values"
        ):
            if "messages" in step:
                last_message = step["messages"][-1]
                if hasattr(last_message, "content"):
                    result = last_message.content

        return result if result else "No results"
    except Exception as e:
        return f"Error: {str(e)}"