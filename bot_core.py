# bot_core.py

import torch
import json
import requests
from sentence_transformers import SentenceTransformer, util
from scraper_module import add_url, load_scraped_data
import re

# Load sentence transformer model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Embed scraped questions
def refresh_embeddings():
    global combined_data, embeddings, answers, all_texts, url_list
    with open("scraped_data.json", "r", encoding="utf-8") as f:
        combined_data = json.load(f)
    all_texts = []
    answers = []
    url_list = []
    for entry in combined_data:
        text = entry.get("answer", "")
        all_texts.append(text)
        answers.append(text)
        url_list.append(entry.get("url", ""))
    embeddings = embed_model.encode(all_texts, convert_to_tensor=True)

refresh_embeddings()

conversation_history = []
START_MESSAGE = (
    "Hello! I'm Assistbot, the digital assistant for Better Analytics. "
    "How can I help you today? If you have any questions about our company, services, or team, just ask!"
)
SYSTEM_PROMPT = (
    "You are Assistbot, an assistant to guide customers."
    "Answer user questions in a professional and helpful tone. "
    "Do not make up your own answers. Keep it short and crisp."
)

def query_ollama_mistral(prompt):
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=30
        )
        return res.json()["response"].strip()
    except Exception as e:
        return f"[Ollama Error] {str(e)}"

def lookup_knowledge(user_input):
    user_embedding = embed_model.encode(user_input, convert_to_tensor=True)
    scores = util.cos_sim(user_embedding, embeddings)[0]
    top_idx = torch.argmax(scores).item()
    return answers[top_idx], scores[top_idx].item(), url_list[top_idx]

def respond(user_input):
    urls = re.findall(r'https?://\S+', user_input)
    for url in urls:
        print(add_url(url))
    refresh_embeddings()
    answer, score, url = lookup_knowledge(user_input)
    conversation_history.append(f"User: {user_input}")
    # Add last bot answer to history (if not first turn)
    if len(conversation_history) > 1:
        conversation_history.append(f"Bot: {answer}")
    # Build context for Mistral
    history = '\n'.join(conversation_history[-6:])  # last 3 turns
    if not answer or score < 0.3:
        context = "No relevant information found in the company data."
    else:
        context = f"{answer}\n(Source: {url})"
    prompt = (
        "You are Assistbot, the official digital assistant for Better Analytics, a technology company. "
        "Whenever the user refers to 'the company', 'this company', or similar terms, always interpret it as referring to Better Analytics. "
        "Always answer using only the provided context. "
        "If the context does not answer the user's question, politely say you don't know. "
        "Be concise, professional, and helpful.\n"
        f"Context: {context}\n"
        f"Conversation history:\n{history}\n"
        f"User question: {user_input}"
    )
    response = query_ollama_mistral(prompt)
    conversation_history.append(f"Bot: {response}")
    return response

if __name__ == "__main__":
    print(START_MESSAGE)
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit", "bye"]:
            print("Bot: Goodbye! If you have more questions about Better Analytics, feel free to return anytime.")
            break
        bot_response = respond(user_input)
        print(f"Bot: {bot_response}")
