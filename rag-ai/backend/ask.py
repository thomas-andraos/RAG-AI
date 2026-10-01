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
    # Remove surrounding whitespace before validating or sending the query onward.
    query = user_query.strip()
    if not query:
        raise ValueError("The query cannot be empty.")

    # Load credentials from the .env file beside this script, then read the Gemini API key.
    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(f"Missing GEMINI_API_KEY in {ENV_PATH}")

    # Create the Gemini client with a 20-second request timeout and up to three attempts.
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

    # Open the local ChromaDB store and its collection of indexed document chunks.
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    # Find the four chunks most relevant to the question and combine their text as context.
    results = collection.query(query_texts=[query], n_results=4)
    documents = (results.get("documents") or [[]])[0]
    context = "\n\n".join(documents)

    # Tell the model to answer only from retrieved material and admit when it is insufficient.
    prompt = (
        "You are a helpful assistant that answers using the provided "
        "documents. If the documents do not contain the answer, respond "
        "with 'I don't know'.\n"
        f"The data:\n{context}\n\nUser question: {query}"
    )

    # Generate the response using the Gemini 3.6 model.
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True,
            ),
        ),
    )
    # Use a fallback if the API response has no text content.
    return response.text or "I don't know."


