import os
import warnings
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
import streamlit as st


warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()


def create_chart(user_prompt: str):
    llm = AzureChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        model="gpt-4o",
        temperature=0
        # timeout=None
    )

    fig = ""
    tool = PythonAstREPLTool(locals={"fig": fig}, globals={"df": df}, verbose=True)
    llm_with_tools = llm.bind_tools([tool], tool_choice=tool.name)
    parser = JsonOutputKeyToolsParser(key_name=tool.name, first_tool_only=True)

    system = f"""You only have access to a pandas dataframe `df`.
    Here is the output of `df.head()`:

    \`\`\`
    {df.head().to_markdown()}
    \`\`\`

    Given a user question, write the Python code to generate a Plotly figure object using the dataframe `df` only.
    Only create any new variables for intermediate steps required for plotting.
    Do NOT generate or simulate new data.
    Return ONLY the valid Python code with Plotly figure object using `df` dataframe and nothing else.
    Do not call `fig.show()`, `plt.show()` functions.
    Don't assume you have access to any libraries other than built-in Python ones, pandas, and plotly.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{question}")
    ])
    chain = prompt | llm_with_tools | parser
    result = chain.invoke({"question": user_prompt}, verbose=True)
    print("\n####################################\n")
    print(user_prompt)
    print(result['query'])
    print("\n####################################\n")
    fig = tool.invoke(result['query'])
    return fig


st.set_page_config(page_title="Data Query & Visualization App", layout="wide")

st.title("📊 Data Query & Visualization App")

# 1. File upload
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file into DataFrame
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.success("✅ File uploaded successfully!")
    st.write("### Data Preview:")
    st.dataframe(df)

    # 2. Query input
    st.write("### Run a Pandas Query")
    query_str = st.text_input(
        "Enter prompt"
    )

    # 3. Execute query
    if query_str:
        try:
            filtered_df = df
            # st.write("### Query Results:")
            # st.dataframe(filtered_df)
            # 4. Plotly chart
            st.write("### Plotly Chart")
            fig = create_chart(query_str)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Invalid query: {e}")
            filtered_df = df
    else:
        filtered_df = df

else:
    st.info("Please upload a file to get started.")


# Prompts:
# Plot a bar chart showing the total number of orders per user.
# plot a scatter chart showing the total number of orders per user.
# Plot a line chart showing the total number of orders per user over time.
# Plot a pie chart showing the distribution of orders by user.