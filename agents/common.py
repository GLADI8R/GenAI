

from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

# define state for the agent
# This is a TypedDict that defines the structure of the state dictionary used in the agent.
class State(TypedDict , total=False ):  # <--- add total=False This tells Python and Pydantic that not all fields are required, so you can pass partial state dictionaries without validation errors.
    def __init__(self):
        self.messages = []
        self.query_retry = 0

    messages: Annotated[list, add_messages]
    question: str
    query: str
    result: str
    answer: str  
    output : str
    chart_type : str
    from_query : bool
    query_retry: int


# define query output for the agent
class QueryOutput(TypedDict):
    """Generated DB query."""

    query: Annotated[str, ..., "Syntactically valid database query."]