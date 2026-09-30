from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

ENV_PATH = Path(__file__).resolve().with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

# setting the environment
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("INSTALLER_RAG")

# Load PDF files from the specified directory
loader = PyPDFDirectoryLoader(DATA_PATH)
raw_documents = loader.load()

# Split the documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300, 
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=True)

chunks = text_splitter.split_documents(raw_documents)

# Prepare the chunks for the ChromaDB collection

documents = []
metadatas = []
ids = []

i = 0

for chunk in chunks:
    documents.append(chunk.page_content)
    metadatas.append(chunk.metadata)
    ids.append(str(i))
    i += 1

# Upsert the documents into the ChromaDB collection

collection.upsert(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)
