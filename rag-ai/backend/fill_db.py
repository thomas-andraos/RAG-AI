from pathlib import Path 
import chromadb
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Find the .env file and add values to the process environment
ENV_PATH = Path(__file__).resolve().with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

DATA_PATH = r"data"  # Directory containing PDF files.
CHROMA_PATH = r"chroma_db"  # Directory where ChromaDB persists its database files.

# Open or create a ChromaDB database at CHROMA_PATH.
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Get the named collection, creating it if it does not already exist.
collection = chroma_client.get_or_create_collection("INSTALLER_RAG")

# Create a loader for PDF files found in DATA_PATH.
loader = PyPDFDirectoryLoader(DATA_PATH)
# Read the PDFs into document objects, including their page content and metadata.
raw_documents = loader.load()

# Configure how each loaded document is divided into smaller chunks.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  # characters per chunk.
    chunk_overlap=100,  # Repeat 100 characters between chunks for context.
    length_function=len,  # Measure chunk size.
    is_separator_regex=True)

# Split documents into chunks
chunks = text_splitter.split_documents(raw_documents)
documents = []  # text content for each chunk.
metadatas = []  # source metadata for eachchunk.
ids = []  # Chunk IDs
i = 0 

for chunk in chunks:  # Process each text chunk produced by the splitter and store its content, metadata, and ID.
    documents.append(chunk.page_content)  
    metadatas.append(chunk.metadata) 
    ids.append(str(i))
    i += 1

# Insert new records or update existing records with the same IDs in the collection.
collection.upsert(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)
