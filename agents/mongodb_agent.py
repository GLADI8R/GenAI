import os
import warnings
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain_mongodb.agent_toolkit import MongoDBDatabase
from langchain_mongodb.agent_toolkit.tool import QueryMongoDBCheckerTool, QueryMongoDBDatabaseTool
from pymongo import MongoClient
from agents import llm
from agents.templates import classification_prompt, mongodb_query_generator_prompt, user_prompt, test_query
from agents.common import State, QueryOutput


warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()


config_memory = {"configurable": {"thread_id": "1"}}
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = "sales"


def detect_intent(user_input: str) -> str:
    try:
        prompt = classification_prompt.invoke({"input": user_input},config=config_memory)
        result = llm.invoke(prompt ,config=config_memory)
        print(f"result ** {result}")
        intent = result.content.strip().lower()
        print(f" ********* detect_intent  intent value is **{intent}**   ")
        if intent not in ["database", "chart"]:
            return "other"
        return intent
    except Exception as e:
        print("❌ Intent detection failed:", e)
        return "other"


class MongoDBAgent():
    def __init__(self, llm):
        """Initialize the MongoDB Agent."""

        print("Initializing MongoDB Agent...")
        if not MONGO_URI:
            raise ValueError("MONGO_URI environment variable is not set.")
        self.db = MongoDBDatabase(
            client=MongoClient(MONGO_URI),
            database=MONGO_DB_NAME
        )

        self.llm = llm


    def write_query(self, state: State) -> dict:
        """Generate MongoDB query to fetch information."""

        print(f" Generating query..." )
        try:
            question = state.get("question")
            if not question:
                messages = state.get("messages", [])
                if messages and isinstance(messages[-1], HumanMessage):
                    question = messages[-1].content

            query_prompt_template = ChatPromptTemplate([
                ("system", mongodb_query_generator_prompt),
                ("user", user_prompt)
            ])

            prompt = query_prompt_template.invoke(
                {
                    "top_k": 5,
                    "db_context": self.db.get_context(),
                    "input": question,
                },
                config=config_memory
            )
            structured_llm = self.llm.with_structured_output(QueryOutput)
            result = structured_llm.invoke(prompt, config=config_memory)
            print(" Generated query successfully.")
            return {"query": result["query"]}
        except Exception as e:
            print(" ❌ Query Generation failure:\n", e)
            return {"query": ""}


    def check_query(self, state: State) -> dict:
        """Check MongoDB query for correctness."""

        try:
            print(" Checking query...")
            if not state.get("query"):
                return {"result": "No query to check."}
            execute_query_tool = QueryMongoDBCheckerTool(
                db=self.db,
                llm=self.llm,
                description='\n    Check if the query is correct.\n    If the query is not correct, an error message will be returned.\n    If an error is returned, rewrite the query, check the query, and try again.\n    '
            )
            result = execute_query_tool.invoke(state["query"], config=config_memory)
            # flag to indicate if the query is valid
            is_valid = False
            if result.content[1:7] == "python" or result.content[3:9] == "python" or result.content[1:5] == "json" or result.content[3:7] == "json":
                is_valid = True

            return {"result": result, "query_valid": is_valid}
        except Exception as e:
            print(" ❌ Query Check failure:\n", e)
            return {"result": ""}


    def execute_query(self, state: State) -> dict:
        """Execute MongoDB query."""
        try:
            print(" Executing query...")
            execute_query_tool = QueryMongoDBDatabaseTool(
                db=self.db,
                description = '\n    Execute a MongoDB query against the database and get back the result..\n    If the query is not correct, an error message will be returned.\n    If an error is returned, rewrite the query, check the query, and try again.\n    '
            )
            return {"result": execute_query_tool.invoke(state["query"],config=config_memory)}
        except Exception as e:
            print(" ❌ Query Execution failure:\n", e)
            return {"result": ""}


# Example usage of the MongoDBAgent
mongodb_agent = MongoDBAgent(llm=llm)
state = State()
state["question"] = test_query
result = mongodb_agent.write_query(state)
state.update(result)
# print("✅ write_query output:", result['query'])

# Check query
result1 = mongodb_agent.check_query(state)
state.update(result1)
# print("✅ check_query output:", result1)

# Execute query
result2 = mongodb_agent.execute_query(state)
state.update(result2)
print("✅ execute_query output:", result2["result"])
