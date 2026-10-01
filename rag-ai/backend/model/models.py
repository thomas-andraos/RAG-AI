from pydantic import BaseModel
from typing import List


# Data shape for a user account.
class User(BaseModel):
    id: int
    username: str
    password: str
    email: str


# Request body accepted when a client sends a message.
class MessageCreate(BaseModel):
    content: str  


# One message stored in a chat and returned by the API.
class Message(BaseModel):
    id: int 
    chatid: int
    sender: str
    content: str
    timestamp: str


# Response model containing both messages produced by one user turn.
class ChatTurn(BaseModel):
    user_message: Message
    assistant_message: Message


# Collection of messages belonging to a chat session.
class History(BaseModel):
    msghistory: List[Message]


# Chat session metadata together with its conversation history.
class Chat(BaseModel):
    chatid: int
    title: str
    created_at: str
    updated_at: str
    history: History = None


