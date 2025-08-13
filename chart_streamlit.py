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


def create_chart(user_prompt: str, df: pd.DataFrame):
    llm = AzureChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        model="gpt-4o",
        temperature=0
        # timeout=None
    )

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
    print("\n####################################\n")
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
            # st.write("### Query Results:")
            # st.dataframe(filtered_df)
            # 4. Plotly chart
            st.write("### Plotly Chart")
            fig = create_chart(query_str, df)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Invalid query: {e}")

else:
    st.info("Please upload a file to get started.")


'''
    # Render message history
    for msg in st.session_state.history:
        print(f"🚨 DEBUG: session_state = {msg}")
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)
        ai_response_message = msg

    # Process new input
    if user_input:
        user_msg = HumanMessage(content=user_input)
        with st.chat_message("user"):
            st.markdown(user_msg.content)    
        st.session_state.history.append(user_msg)
        
        # result = app.invoke({"messages": st.session_state.history}, config=config)
        fig = create_chart(user_input, df)
        # st.plotly_chart(fig, use_container_width=True)

        # st.session_state.history = result["messages"]
        # st.session_state.history.append(AIMessage(content=fig, type='chart'))

        # Display the assistant's message
        with st.chat_message("assistant"):
            st.markdown(st.session_state.history[-1].content)

            ai_response_message  = st.session_state.history[-1]
            print("---------------",ai_response_message)
            
            # if 'type' in ai_response_message and ai_response_message['type'] == 'chart':
            #     fig = ai_response_message
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please upload a file to get started.")
'''

# Prompts:
# Plot a bar chart showing the total number of orders per user.
# plot a scatter chart showing the total number of orders per user.
# Plot a line chart showing the total number of orders per user over time.
# Plot a pie chart showing the distribution of orders by user.