import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.callbacks import StreamlitCallbackHandler
from vector import retriever  # Ensure vector.py is properly set up

# Set page config
st.set_page_config(page_title="Jungle Lodges Chatbot", page_icon="🦁")

st.title("🦁 Jungle Lodges Booking Assistant")
st.markdown("Ask any question about **Kabini River Lodge** packages, pricing, or bookings.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Prompt template
template = """
You are a helpful and professional assistant for Jungle Lodges and Resorts bookings.

Only answer based on the context provided below. 
If the answer is not found in the context, reply politely with:

"I'm sorry, but I couldn't find that information in the available booking details. 
You may contact our support team for further assistance."

Context:
{context}

Question:
{question}

Answer:
"""
prompt = ChatPromptTemplate.from_template(template)

# User input
user_input = st.chat_input("Ask your question about the resort...")

if user_input:
    # Save user input to history
    st.session_state.chat_history.append(("user", user_input))

    # Retrieve relevant data
    docs = retriever.invoke(user_input)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt_value = prompt.invoke({"context": context, "question": user_input})

    # Show assistant message container
    with st.chat_message("assistant"):
        container = st.empty()  # ✅ This creates a valid container
        callback_handler = StreamlitCallbackHandler(parent_container=container)

        # Use streaming LLM
        llm = OllamaLLM(model="mistral", streaming=True, callbacks=[callback_handler])
        response = llm.invoke(prompt_value)

        # Show plain response (optional)
        st.write(response)

        # Save to chat history
        st.session_state.chat_history.append(("assistant", response))

# Display chat history
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)
