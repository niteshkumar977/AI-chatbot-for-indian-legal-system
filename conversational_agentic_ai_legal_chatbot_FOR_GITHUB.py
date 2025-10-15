# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import streamlit as st
import openai
import os

# Set your OpenAI API key securely
openai.api_key = 'open API key'

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "context_buffer" not in st.session_state:
    st.session_state.context_buffer = ""
if "temp_input" not in st.session_state:
    st.session_state.temp_input = ""

st.set_page_config(page_title="Agentic Legal Chatbot", layout="centered")
st.title("⚖️ Conversational Agentic Legal Chatbot")
st.markdown("Ask any legal question related to Indian law. You can follow up with more questions — the bot remembers previous answers.")

# Input box using a temporary key
user_input = st.text_input("Your message:", value=st.session_state.temp_input, key="input_box")

# 🧠 Step 1: Classify the query
def classify_query(query: str) -> str:
    system_prompt = "You are a legal classifier. Categorize the query into one of: 'Criminal Law', 'Civil Law', 'Constitutional Law', 'Family Law', 'Corporate Law', or 'Other'."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.3,
        max_tokens=50
    )
    return response['choices'][0]['message']['content'].strip()

# 🧩 Step 2: Plan reasoning steps
def plan_steps(category: str, query: str) -> str:
    planner_prompt = f"""
You are a legal planning agent. Based on the category '{category}', break down the user's query into logical steps to answer it thoroughly. Be specific and methodical.
Query: {query}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal planning agent."},
            {"role": "user", "content": planner_prompt}
        ],
        temperature=0.4,
        max_tokens=50
    )
    return response['choices'][0]['message']['content'].strip()

# 🔍 Step 3: Simulate tool use
def simulate_tool_use(category: str, query: str) -> str:
    tool_prompt = f"""
You are a legal assistant with access to Indian legal databases. Simulate what kind of external sources or tools you would use to answer this query, such as case law, statutes, or government portals.
Category: {category}
Query: {query}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal assistant simulating tool use."},
            {"role": "user", "content": tool_prompt}
        ],
        temperature=0.5,
        max_tokens=50
    )
    return response['choices'][0]['message']['content'].strip()

# 🧾 Step 4: Generate final response with context
def generate_response(query: str, category: str, steps: str, tools: str, context: str) -> str:
    full_prompt = f"""
You are a legal expert in Indian law. Engage in a helpful, conversational tone.

Here is relevant context from previous conversation:
{context}

Current query: {query}

Category: {category}
Reasoning Steps: {steps}
Simulated Tool Use: {tools}

Now, provide a clear, accurate, and legally grounded response to the user's query.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal expert in Indian law."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.5,
        max_tokens=50
    )
    return response['choices'][0]['message']['content'].strip()

# 🔘 Trigger agentic flow
if st.button("Send"):
    if user_input.strip():
        # Append all previous assistant answers to context buffer
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                st.session_state.context_buffer += f"\nPrevious answer: {msg['content']}"

        with st.spinner("Classifying your query..."):
            category = classify_query(user_input)

        with st.spinner(f"Planning steps for {category}..."):
            steps = plan_steps(category, user_input)

        with st.spinner("Simulating tool use..."):
            tools = simulate_tool_use(category, user_input)

        with st.spinner("Generating legal response..."):
            response = generate_response(user_input, category, steps, tools, st.session_state.context_buffer)

        # Update chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

        # Clear input for next turn
        st.session_state.temp_input = ""

# Display conversation
if st.session_state.chat_history:
    st.markdown("### 💬 Conversation")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")


# %%
