import warnings
import asyncio
import pandas as pd
import streamlit as st
from agents.common import detect_intent
from agents.orchestrator import orchestrate


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


if option != "-":

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

        intent = detect_intent(prompt)
        response, code = asyncio.run(orchestrate(
            db_choice=option,
            query=prompt,
            intent=intent
        ))
        if intent =="chart":
            msg = {"role": "assistant", "type": intent, "content": response, "code": code}
            st.session_state.messages.append({"role": "assistant", "type": intent, "content": response, "code": code})
        else:
             st.session_state.messages.append({"role": "assistant", "type": intent, "content": response})

        with st.chat_message("assistant"):
            if intent == "chart":
                st.plotly_chart(response, use_container_width=True)
            elif intent == "database":
                st.dataframe(response)
            else:
                st.write("Unsupported intent type. Please try again with a valid query.")


# Prompts:
# What are the names of the top 3 users with highest total purchase amount (quantity * price)?
# Plot a bar chart showing the total number of orders for each user.
# Plot a scatter chart showing the total number of orders per user.
# Plot a line chart showing the total number of orders per user over time.
# Plot a pie chart showing the distribution of orders by user.