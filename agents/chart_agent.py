import os
import warnings
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from agents import llm


warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()


def create_chart(user_prompt: str, df: pd.DataFrame):
    fig = ""
    tool = PythonAstREPLTool(locals={"fig": fig}, globals={"df": df})
    llm_with_tools = llm.bind_tools([tool], tool_choice=tool.name)
    parser = JsonOutputKeyToolsParser(key_name=tool.name, first_tool_only=True)

    system = f"""You only have access to a pandas dataframe `df`.
    Here is the output of `df.head()` for reference:

    \`\`\`
    {df.head().to_markdown()}
    \`\`\`

    Do NOT generate or simulate new data.
    Given a user question, write the Python code to generate a Plotly figure object using the dataframe `df` as reference for code generation.
    Only create any new variables for intermediate steps required for plotting.
    Return ONLY the valid Python code with Plotly figure object and nothing else.
    Do not call `fig.show()`, `plt.show()` functions.
    Don't assume you have access to any libraries other than built-in Python ones, pandas, and plotly.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{question}")
    ])
    chain = prompt | llm_with_tools | parser
    result = chain.invoke({"question": user_prompt}, verbose=True)
    # print("\n####################################\n")
    # print(result['query'])
    # print("\n####################################\n")
    fig = tool.invoke(result['query'])
    return fig
