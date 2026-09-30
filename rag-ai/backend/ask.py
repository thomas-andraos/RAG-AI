import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


ENV_PATH = Path(__file__).resolve().with_name(".env")
CHROMA_PATH = Path(__file__).resolve().with_name("chroma_db")
COLLECTION_NAME = "INSTALLER_RAG"


def generate_response(user_query: str) -> str:
    """Retrieve relevant documents and generate an answer for a user query."""
    query = user_query.strip()
    if not query:
        raise ValueError("The query cannot be empty.")

    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(f"Missing GEMINI_API_KEY in {ENV_PATH}")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=20_000,
            retry_options=types.HttpRetryOptions(
                attempts=3,
                initial_delay=1,
                max_delay=3,
            ),
        ),
    )
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    results = collection.query(query_texts=[query], n_results=4)
    documents = (results.get("documents") or [[]])[0]
    context = "\n\n".join(documents)

    prompt = (
        "You are a helpful assistant that answers using the provided "
        "documents. If the documents do not contain the answer, respond "
        "with 'I don't know'.\n"
        f"The data:\n{context}\n\nUser question: {query}"
    )
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True,
            ),
        ),
    )
    return response.text or "I don't know."


if __name__ == "__main__":
    print(generate_response(input("Enter your query: ")))


