import { useState } from 'react';
import api from '../api';

// Chat interface for composing questions and displaying the conversation.
function Chats() {
  // Keep the active chat and unsent text in component state.
  const [chat, setChat] = useState(null);
  const [draft, setDraft] = useState('');
  // Track request status so duplicate sends can be prevented and errors shown.
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');

  // Create a chat on the first send, then post each message to that chat.
  const sendMessage = async (event) => {
    event.preventDefault();
    const content = draft.trim();
    if (!content || sending) return;

    setSending(true);
    setError('');
    try {
      // Reuse the active chat, or create one when this is the first message.
      const activeChat = chat ?? (await api.post('/chathistory')).data;
      if (!chat) setChat(activeChat);

      // Send the message and add both the user's message and assistant reply to the UI.
      const response = await api.put(`/chathistory/${activeChat.chatid}`, { content });
      setChat({
        ...activeChat,
        updated_at: response.data.assistant_message.timestamp,
        history: {
          msghistory: [
            ...activeChat.history.msghistory,
            response.data.user_message,
            response.data.assistant_message,
          ],
        },
      });
      setDraft('');
    } catch (requestError) {
      // Show the backend's error detail when available, otherwise use a generic message.
      console.error('Could not send message:', requestError);
      setError(requestError.response?.data?.detail || 'Could not send message.');
    } finally {
      // Re-enable sending whether the request succeeded or failed.
      setSending(false);
    }
  };

  return (
    <main className="chat-app">
      {/* Identify the assistant and the subject area of its answers. */}
      <header className="chat-title">
        <h1>RAG AI Bot</h1>
        <p>Ask questions about your installation documents.</p>
      </header>

      {/* Render each message, or show the empty state before the first message. */}
      <ol className="message-history" aria-live="polite">
        {chat?.history.msghistory.map((message) => (
          <li className={`message ${message.sender}`} key={message.id}>
            <strong>{message.sender}</strong>
            <p>{message.content}</p>
          </li>
        ))}
        {!chat?.history.msghistory.length && (
          <li className="empty-history">No messages yet. Ask your first question.</li>
        )}
      </ol>

      {/* Present request errors separately from the conversation. */}
      {error && <p className="error" role="alert">{error}</p>}
      {/* Submit the draft on Enter/button submission and disable sending while busy. */}
      <form className="message-form" onSubmit={sendMessage}>
        <textarea
          aria-label="Message"
          disabled={sending}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Write a message..."
          rows={2}
          value={draft}
        />
        <button disabled={!draft.trim() || sending} type="submit">
          {sending ? 'Sending...' : 'Send'}
        </button>
      </form>
    </main>
  );
}

export default Chats;
