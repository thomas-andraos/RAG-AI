from datetime import datetime

from ask import generate_response
from model.models import Chat, ChatTurn, History, Message


class ChatService:
    def __init__(self):
        self.memory_db = {"chathistory": []}

    def create_chat_session(self, title: str = "New Chat") -> Chat:
        # Assign the next ID
        chat_id = len(self.memory_db["chathistory"]) + 1
        now = datetime.now().isoformat()

        # Build an empty chat session
        chat = Chat(
            chatid=chat_id,
            title=title,
            created_at=now,
            updated_at=now,
            history=History(msghistory=[])
        )

        # Save the new session
        self.memory_db["chathistory"].append(chat)
        return chat

    def add_message_to_chat(self, chatid: int, content: str) -> ChatTurn:
        # Find the target session
        chat = next(
            (
                chat
                for chat in self.memory_db["chathistory"]
                if chat.chatid == chatid
            ),
            None,
        )
        if chat is None:
            raise ValueError(f"Chat with id {chatid} not found.")

        # Create and store the user's message before asking the assistant to respond.
        now = datetime.now().isoformat()

        msg = Message(
            id=len(chat.history.msghistory) + 1,
            chatid=chatid,
            sender="user",
            content=content,
            timestamp=now
        )
        chat.history.msghistory.append(msg)

        # Generate the assistant reply from the user's text and add it to the same history.
        response_msg = Message(
            id=len(chat.history.msghistory) + 1,
            chatid=chatid,
            sender="assistant",
            content=generate_response(content),
            timestamp=now
        )
        chat.history.msghistory.append(response_msg)

        # Refresh the session's last-updated time and return both messages as one chat turn.
        chat.updated_at = datetime.now().isoformat()
        return ChatTurn(
            user_message=msg,
            assistant_message=response_msg,
        )

    def get_chat_history(self):
        # Return all chat sessions currently held in memory.
        return self.memory_db["chathistory"]
    
