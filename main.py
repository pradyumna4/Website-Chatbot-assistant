from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from vector import retriever
import time
import sys


def typing_animation():
    print("\n Typing", end='', flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print(".", end='', flush=True)
    print("\n")  

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


llm = OllamaLLM(
    model="mistral",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)


while True:
    question = input("\nAsk a question (type 'exit' to quit): ")
    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt_value = prompt.invoke({"context": context, "question": question})

    
    typing_animation()

    
    llm.invoke(prompt_value)
