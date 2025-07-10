from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

# Load your data
loader = TextLoader("data.txt")
docs = loader.load()

# Split the text into chunks for embedding
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = splitter.split_documents(docs)

# Set up embeddings using a local Ollama model
embedding = OllamaEmbeddings(model="mxbai-embed-large")

# Create or load the vector database
db = Chroma.from_documents(texts, embedding, persist_directory="db")
db.persist()  # Save the vector store to disk

# Export retriever so it can be used in app.py
retriever = db.as_retriever()
