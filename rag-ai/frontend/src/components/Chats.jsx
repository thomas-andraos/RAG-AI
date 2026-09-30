import { useEffect, useState } from 'react';
import api from '../api';

function Chats() {
  const [chat, setChat] = useState(null);
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const createChat = async () => {
      try {
        const response = await api.post('/chathistory');
        setChat(response.data);
      } catch (requestError) {
        console.error('Could not create chat:', requestError);
        setError('Could not start the chat.');
      } finally {
        setLoading(false);
      }
    };

    createChat();
  }, []);

  const sendMessage = async (event) => {
    event.preventDefault();
    const content = draft.trim();
    if (!chat || !content || sending) return;

    setSending(true);
    setError('');
    try {
      const response = await api.put(`/chathistory/${chat.chatid}`, { content });
      setChat((currentChat) => ({
        ...currentChat,
        updated_at: response.data.assistant_message.timestamp,
        history: {
          msghistory: [
            ...currentChat.history.msghistory,
            response.data.user_message,
            response.data.assistant_message,
          ],
        },
      }));
      setDraft('');
    } catch (requestError) {
      console.error('Could not send message:', requestError);
      setError(requestError.response?.data?.detail || 'Could not send message.');
    } finally {
      setSending(false);
    }
  };

  if (loading) return <main className="chat-app">Starting chat...</main>;

  return (
    <main className="chat-app">
      <header className="chat-title">
        <h1>RAG AI Bot</h1>
        <p>Ask questions about your installation documents.</p>
      </header>

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

      {error && <p className="error" role="alert">{error}</p>}
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
