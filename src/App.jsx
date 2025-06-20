import React, { useState, useRef, useEffect } from 'react';

const App = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const inputRef = useRef(null);
  const bottomRef = useRef(null); 

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (trimmed === '') return;
  
    const userMessage = { type: 'user', text: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
  
    try {
      const res = await fetch('http://localhost:5001/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed }),
      });
  
      const data = await res.json();
      const botReply = { type: 'bot', text: data.answer || '[No answer returned]' };
      setMessages((prev) => [...prev, botReply]);
    } catch (error) {
      console.error('Backend error:', error);
      setMessages((prev) => [...prev, { type: 'bot', text: 'I am experiencing technical difficulties. Please try again later.' }]);
    }
  };
  

  const handleInputChange = (e) => {
    setInput(e.target.value);

    const el = inputRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = el.scrollHeight + 'px';
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'auto' });
    }
  }, [messages]);

  return (
    <div className="app-container">
      <h1 className="title">HR Chatbot</h1>
      <p className="subtitle">Type a message and press Enter or tap the arrow</p>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={msg.type === 'user' ? 'user-message' : 'bot-message'}
          >
            {msg.text}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          ref={inputRef}
          className="chat-input"
          placeholder="Type a message..."
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
        />
        <button className="send-button" onClick={sendMessage}>
          ⬆
        </button>
      </div>
    </div>
  );
};

export default App;
