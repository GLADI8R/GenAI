from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from agents import llm
from agents.templates import classification_prompt

# define state for the agent
# This is a TypedDict that defines the structure of the state dictionary used in the agent.
class State(TypedDict , total=False ):  # <--- add total=False This tells Python and Pydantic that not all fields are required, so you can pass partial state dictionaries without validation errors.
    def __init__(self):
        self.messages = []
        self.query_retry = 0

    messages: Annotated[list, add_messages]
    question: str
    intent: str
    query: str
    columns: list
    result: str
    answer: str  
    output: str
    chart_type: str
    from_query: bool
    query_retry: int


# define query output for the agent
class QueryOutput(TypedDict):
    """Generated DB query."""

    query: Annotated[str, ..., "Syntactically valid database query."]
    columns: Annotated[list, ..., "List of column names in the query result."]

config_memory = {"configurable": {"thread_id": "1"}}

def detect_intent(user_input: str) -> str:
    try:
        prompt = classification_prompt.invoke({"input": user_input},config=config_memory)
        result = llm.invoke(prompt ,config=config_memory)
        intent = result.content.strip().lower()
        if intent not in ["database", "chart"]:
            return "other"
        return intent
    except Exception as e:
        print("❌ Intent detection failed:", e)
        return "other"
