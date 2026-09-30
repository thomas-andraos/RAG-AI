import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.models import Chat, ChatTurn, History, MessageCreate
from service.chat_service import ChatService

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService()


@app.get("/chathistory", response_model=History)
def get_chat_history():
    return History(chathistory=chat_service.get_chat_history())


@app.post("/chathistory", response_model=Chat)
def create_new_chat():
    return chat_service.create_chat_session(title="New Chat")


@app.put("/chathistory/{chatid}", response_model=ChatTurn)
def add_message_to_chat(chatid: int, message: MessageCreate):
    return chat_service.add_message_to_chat(
        chatid=chatid,
        content=message.content,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
