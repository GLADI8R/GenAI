import warnings
import pandas as pd
import streamlit as st
from agents import llm
from agents.chart_agent import create_chart
from agents.sqlite_agent import SQLAgent
from agents.mongodb_agent import MongoDBAgent
from agents.common import State, detect_intent


warnings.filterwarnings("ignore", category=UserWarning)

## *******************************************************  Streamlit app setup  *******************************************************
st.set_page_config(page_title="Data Query & Visualization App", layout="wide")

# Set up sidebar title
st.sidebar.header("Upload File")

option = st.sidebar.selectbox(
    "Choose an option:",
    ("-", "MongoDB", "SQL", "File Upload")
)

# Initialize session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

agent, state = None, None

if option == "File Upload":
    st.sidebar.info("Please upload a file to continue.")
    # File upload
    uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv", "xlsx"])

    file_content = None
    if uploaded_file:
        # Read file into DataFrame
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                file_content = df.head().to_string()
        except Exception as e:
            st.error(f"Error reading file: {e}")
            # st.stop()

    if file_content:
        st.success("✅ File uploaded successfully!")
        st.write("### Data Preview:")
        st.dataframe(df)

    # Display existing messages
    st.write("📜 Chat with Assistant")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            st.plotly_chart(msg["content"], use_container_width=True)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        fig = create_chart(prompt, df)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": fig})
        with st.chat_message("assistant"):
            st.plotly_chart(fig, use_container_width=True)

if option == "SQL":
    agent = SQLAgent(llm=llm)
    state = State()

    # Display existing messages
    st.write("📜 Chat with Assistant")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            if msg["type"] == "chart":
                st.plotly_chart(msg["content"], use_container_width=True)
            else:
                st.dataframe(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        state["question"] = prompt

        intent = detect_intent(prompt)

        result = agent.write_query(state)
        state.update(result)
        result1 = agent.check_query(state)
        state.update(result1)
        result2 = agent.execute_query(state)
        state.update(result2)
        # print("✅ execute_query output:", result2["result"], "\n columns:", state.get("columns", []))
        
        df = pd.DataFrame(data=eval(state.get("result")), columns=state.get("columns"))
        fig = None
        if intent =="chart":
            fig = create_chart(prompt, df)
            msg = {"role": "assistant", "type": intent, "content": fig}
            st.session_state.messages.append({"role": "assistant", "type": intent, "content": fig})
        else:
             st.session_state.messages.append({"role": "assistant", "type": intent, "content": df})

        with st.chat_message("assistant"):
            if intent == "chart":
                st.plotly_chart(fig, use_container_width=True)
            elif intent == "database":
                st.dataframe(df)
            else:
                st.write("Unsupported intent type. Please try again with a valid query.")

if option == "MongoDB":
    agent = MongoDBAgent(llm=llm)
    state = State()

    # Display existing messages
    st.write("📜 Chat with Assistant")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            if msg["type"] == "chart":
                st.plotly_chart(msg["content"], use_container_width=True)
            else:
                st.dataframe(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        state["question"] = prompt

        intent = detect_intent(prompt)

        result = agent.write_query(state)
        state.update(result)
        result1 = agent.check_query(state)
        state.update(result1)
        result2 = agent.execute_query(state)
        state.update(result2)
        # print("✅ execute_query output:", result2["result"], "\n columns:", state.get("columns", []))
        
        df = pd.DataFrame(data=eval(state.get("result")))
        fig = None
        if intent =="chart":
            fig = create_chart(prompt, df)
            msg = {"role": "assistant", "type": intent, "content": fig}
            st.session_state.messages.append({"role": "assistant", "type": intent, "content": fig})
        else:
             st.session_state.messages.append({"role": "assistant", "type": intent, "content": df})
        
        with st.chat_message("assistant"):
            if intent == "chart":
                st.plotly_chart(fig, use_container_width=True)
            elif intent == "database":
                st.dataframe(df)
            else:
                st.write("Unsupported intent type. Please try again with a valid query.")

# Prompts:
# What are the names of the top 3 users with highest total purchase amount (quantity * price)?
# Plot a bar chart showing the total number of orders for each user.
# Plot a scatter chart showing the total number of orders per user.
# Plot a line chart showing the total number of orders per user over time.
# Plot a pie chart showing the distribution of orders by user.