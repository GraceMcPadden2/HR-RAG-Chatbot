import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  const sendMessage = () => {
    if (input.trim() !== '') {
      setMessages([...messages, input.trim()]);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-container">
      <h1 className="title">My Simple Chat</h1>
      <p className="subtitle">Type a message and press Enter or click Send</p>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className="user-message">
            {msg}
          </div>
        ))}
      </div>

      <div className="input-area">
        <textarea
          className="input-box"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <button className="send-button" onClick={sendMessage}>
          ➤
        </button>
      </div>
    </div>
  );
};

export default App;
