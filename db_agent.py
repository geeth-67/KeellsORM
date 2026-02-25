from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

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
from langgraph.checkpoint.postgres import PostgresSaver

POSTGRES_CHECKPOINT_URL = "postgresql://cclarke:admin@localhost:5432/keells"

checkpointer_cm = PostgresSaver.from_conn_string(
    POSTGRES_CHECKPOINT_URL
)

checkpointer = checkpointer_cm.__enter__()

checkpointer.setup()

sql_agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer
)


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