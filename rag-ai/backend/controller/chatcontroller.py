import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.models import Chat, ChatTurn, History, MessageCreate
from service.chat_service import ChatService

# Create the FastAPI application that serves the chat endpoints.
app = FastAPI()

# Allow the local Vite frontend to make browser requests to this backend.
origins = [
    "http://localhost:5173",
]

# Configure cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep one service instance so its in-memory chats are shared across requests.
chat_service = ChatService()


# Endpoint intended to expose the chat history held by the service.
@app.get("/chathistory", response_model=History)
def get_chat_history():
    return History(chathistory=chat_service.get_chat_history())


# Create a new chat session and return its details to the client.
@app.post("/chathistory", response_model=Chat)
def create_new_chat():
    return chat_service.create_chat_session(title="New Chat")


# Add a user message to the requested chat and return the user/assistant message pair.
@app.put("/chathistory/{chatid}", response_model=ChatTurn)
def add_message_to_chat(chatid: int, message: MessageCreate):
    return chat_service.add_message_to_chat(
        chatid=chatid,
        content=message.content,
    )


if __name__ == "__main__":
    # Start the development server when this module is run directly.
    uvicorn.run(app, host="0.0.0.0", port=8000)
