import os
import warnings
import pandas as pd
import json
import plotly.express as px
import plotly.io as pio
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from fastmcp import FastMCP
from agents import llm


warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

chart_mcp = FastMCP(name="ChartAgent", host="0.0.0.0", port=8003)

@chart_mcp.tool()
def create_chart(user_prompt: str, df: list):
    """
    Create a chart based on user prompt and DataFrame.
    
    Args:
        user_prompt (str): The user's question or prompt for the chart.
        df (list): DataFrame data as a list of dictionaries.

    Returns:
        str: JSON representation of the Plotly figure.
        str: The generated Python code used to create the chart.
    """
    try:
        df = pd.DataFrame(df)
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
        return pio.to_json(fig), result['query']
    except Exception as e:
        print("❌ Error in create_chart:", e)
        return None, None


if __name__ == "__main__":
    chart_mcp.run(transport="http")