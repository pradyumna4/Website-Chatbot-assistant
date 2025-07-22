# bot_core.py

import torch
import json
import requests
from sentence_transformers import SentenceTransformer, util
from scraper_module import add_url, load_scraped_data
from translator import translate
import re

# Load multilingual sentence transformer model
embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Embed scraped questions
def refresh_embeddings():
    global combined_data, embeddings, answers, all_questions, question_to_answer_idx
    with open("scraped_data.json", "r", encoding="utf-8") as f:
        combined_data = json.load(f)
    all_questions = []
    answers = []
    question_to_answer_idx = []
    for idx, entry in enumerate(combined_data):
        for q in entry.get("questions", []):
            all_questions.append(q.lower().strip())
            answers.append(entry["answer"])
            question_to_answer_idx.append(idx)
    embeddings = embed_model.encode(all_questions, convert_to_tensor=True)

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
    return answers[top_idx], scores[top_idx].item(), question_to_answer_idx[top_idx]

def respond(user_input, user_lang="en"):  # user_lang: ISO code, e.g. 'hi', 'en', 'ta'
    # Always process and answer in English
    print(f"[DEBUG] Original input: {user_input}")
    print(f"[DEBUG] Input language: {user_lang}")
    
    user_input_en = translate(user_input, user_lang, "en")
    print(f"[DEBUG] Translated to English: {user_input_en}")
    
    # Check for translation errors
    if user_input_en.startswith("[Translation Error]"):
        return "Sorry, I had trouble understanding your message. Please try again or use English."
    
    urls = re.findall(r'https?://\S+', user_input_en)
    for url in urls:
        print(add_url(url))
    refresh_embeddings()
    answer, score, idx = lookup_knowledge(user_input_en)
    conversation_history.append(f"User: {user_input_en}")
    if len(conversation_history) > 1:
        conversation_history.append(f"Bot: {answer}")
    history = '\n'.join(conversation_history[-6:])  # last 3 turns
    prompt = (
        "You are Assistbot, the official digital assistant for Better Analytics, a technology company. "
        "Whenever the user refers to 'the company', 'this company', or similar terms, always interpret it as referring to Better Analytics. "
        "Always answer using only the provided context. "
        "If the context does not answer the user's question, politely say you don't know. "
        "Be concise, professional, and helpful.\n"
        f"Context: {answer}\n"
        f"Conversation history:\n{history}\n"
        f"User question: {user_input_en}"
    )
    response_en = query_ollama_mistral(prompt)
    # Handle Ollama errors gracefully
    if response_en.startswith("[Ollama Error]"):
        print(response_en)  # Log the error for debugging
        response_en = "Sorry, I'm having trouble connecting to the server. Please try again later."
    conversation_history.append(f"Bot: {response_en}")
    # Always return the response in English, regardless of user_lang
    return response_en

if __name__ == "__main__":
    print(START_MESSAGE)
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit", "bye"]:
            print("Bot: Goodbye! If you have more questions about Better Analytics, feel free to return anytime.")
            break
        bot_response = respond(user_input)
        print(f"Bot: {bot_response}")
