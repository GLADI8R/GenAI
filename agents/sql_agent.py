import os
import warnings
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLCheckerTool, QuerySQLDatabaseTool
from sqlalchemy import create_engine
from fastmcp import FastMCP
from agents import llm
from agents.templates import sql_query_generator_prompt, user_prompt
from agents.common import State, QueryOutput


warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()


config_memory = {"configurable": {"thread_id": "1"}}
SQL_URI = os.getenv("SQL_URI")

sql_mcp = FastMCP(name="SQLAgent", host="0.0.0.0", port=8001)


class SQLAgent():
    def __init__(self, llm):
        """Initialize the SQL Agent."""

        print("Initializing SQL Agent...")
        if not SQL_URI:
            raise ValueError("SQL_URI environment variable is not set.")

        self.db = SQLDatabase(engine=create_engine(SQL_URI))
        self.llm = llm


    def write_query(self, state: State) -> dict:
        """Generate SQL query to fetch information."""

        print(f" Generating query..." )
        try:
            question = state.get("question")
            if not question:
                messages = state.get("messages", [])
                if messages and isinstance(messages[-1], HumanMessage):
                    question = messages[-1].content

            query_prompt_template = ChatPromptTemplate([
                ("system", sql_query_generator_prompt),
                ("user", user_prompt)
            ])

            prompt = query_prompt_template.invoke(
                {
                    "dialect": self.db.dialect,
                    "top_k": 100,
                    "db_context": self.db.get_table_info(),
                    "input": question,
                },
                config=config_memory
            )
            structured_llm = self.llm.with_structured_output(QueryOutput)
            result = structured_llm.invoke(prompt, config=config_memory)
            print(" Generated query successfully.")
            return {"query": result["query"], "columns": result["columns"]}
        except Exception as e:
            print(" ❌ Query Generation failure:\n", e)
            return {"query": ""}


    def check_query(self, state: State) -> dict:
        """Check SQL query for correctness."""

        try:
            print(" Checking query...")
            if not state.get("query"):
                return {"result": "No query to check."}
            execute_query_tool = QuerySQLCheckerTool(
                db=self.db,
                llm=self.llm
            )
            result = execute_query_tool.invoke(state["query"], config=config_memory)
            # flag to indicate if the query is valid
            is_valid = False
            if result[1:4] == "sql" or result[3:6] == "sql":
                is_valid = True

            return {"result": result}
        except Exception as e:
            print(" ❌ Query Check failure:\n", e)
            return {"result": ""}


    def execute_query(self, state: State) -> dict:
        """Execute SQL query."""
        try:
            print(" Executing query...")
            execute_query_tool = QuerySQLDatabaseTool(
                db=self.db
            )
            return {"result": execute_query_tool.run(state["query"],config=config_memory)}
        except Exception as e:
            print(" ❌ Query Execution failure:\n", e)
            return {"result": ""}

@sql_mcp.tool()
def run_sql(query: str) -> State:

    # Example usage of the SQLAgent
    sql_agent = SQLAgent(llm=llm)
    state = State()
    state["question"] = query

    result = sql_agent.write_query(state)
    state.update(result)
    # print("✅ write_query output:", result['query'])

    # Check SQL query
    result1 = sql_agent.check_query(state)
    state.update(result1)
    # print("✅ check_query output:", result1)

    # Execute SQL query
    result2 = sql_agent.execute_query(state)
    state.update(result2)
    # print("✅ execute_query output:", result2["result"], "\n Columns:", state.get("columns", []))

    return state

if __name__ == "__main__":
    sql_mcp.run(transport="http")
