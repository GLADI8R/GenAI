
from langchain.prompts import ChatPromptTemplate

# test_query = "generate only query to find the user ids of top 10 users with highest total purchase amount (quantity * price) from 'orders' collection?"
test_query = "what are the names of the top users with highest total purchase amount (quantity * price)?"

user_prompt = "Question: {input}"

mongodb_query_generator_prompt = """You are an agent designed to interact with a MongoDB database.
Given an input question, create a syntactically correct MongoDB query and return the query.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant field to return the most interesting examples in the database.
Never query for all the fields from a specific collection, only ask for the relevant fields given the question.

The query MUST be of the form: `db.collectionName.aggregate(...)`

Refer the database context below to construct your query.
{db_context}
"""

sql_query_generator_prompt = """You are an agent designed to interact with a {dialect} database.
Given an input question, create a syntactically correct SQL query and return the query.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant field to return the most interesting examples in the database.
Never query for all the fields from a specific table, only ask for the relevant fields given the question.

Refer the database context below to construct your query.
{db_context}
"""

agent_system_prompt = """Answer the following questions as best you can. You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Thought:{agent_scratchpad}"""

classification_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that classifies user input into one of these categories: 'database', 'chart' or 'other'. Respond ONLY with one of these words. Do not explain."),
    ("human", "User: Count the number of customers from table Customer"),
    ("ai", "database"),
    ("human", "User: What are the top 10 products by sales?"),
    ("ai", "database"),
    ("human", "User: create a chart or graph"),
    ("ai", "chart"),
    ("human", "User: Plot a bar chart showing the total number of orders for each user."),
    ("ai", "chart"),
    ("human", "User: Tell me a joke"),
    ("ai", "other"),
    ("human", "User: {input}")
])