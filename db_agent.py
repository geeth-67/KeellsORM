from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

load_dotenv()

DB_URL = "postgresql+asyncpg://cclarke:admin@localhost:5432/keells"

db = SQLDatabase.from_uri(DB_URL)

model = ChatOpenAI(model="gpt-3.5-turbo")
