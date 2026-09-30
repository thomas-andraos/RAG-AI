from pydantic import BaseModel
from typing import List


class User(BaseModel):
    id: int
    username: str
    password: str
    email: str


class MessageCreate(BaseModel):
    content: str


class Message(BaseModel):
    id: int
    chatid: int
    sender: str
    content: str
    timestamp: str


class ChatTurn(BaseModel):
    user_message: Message
    assistant_message: Message


class History(BaseModel):
    msghistory: List[Message]


class Chat(BaseModel):
    chatid: int
    title: str
    created_at: str
    updated_at: str
    history: History = None  # Initialize history as None


