import React, { useState, useEffect } from 'react';
import WelcomeScreen from './components/WelcomeScreen';
import ChatWindow from './components/ChatWindow';

let base_url = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
if (base_url && !base_url.startsWith('http://') && !base_url.startsWith('https://')) {
  base_url = 'https://' + base_url;
}
const API_BASE_URL = base_url;

export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking', 'online', 'offline'
  const [documentCount, setDocumentCount] = useState(0);

  // Check health of backend on mount
  const checkBackendHealth = async () => {
    setBackendStatus('checking');
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'healthy') {
          setBackendStatus('online');
          setDocumentCount(data.document_count || 0);
        } else {
          setBackendStatus('offline');
        }
      } else {
        setBackendStatus('offline');
      }
    } catch (err) {
      setBackendStatus('offline');
    }
  };

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const handleSendMessage = async (text) => {
    const queryText = text || inputValue.trim();
    if (!queryText) return;

    if (!text) {
      setInputValue('');
    }

    // Append user message
    const userMsg = { sender: 'user', text: queryText };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: queryText }),
      });

      if (!response.ok) {
        throw new Error('Server returned an error');
      }

      const data = await response.json();
      
      // Append bot response
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: data.text,
        citation: data.citation,
        refused: data.refused
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: "I encountered a connection issue reaching the facts assistant server. Please check your connection and try again.",
        citation: "",
        refused: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen text-on-surface bg-surface-container-lowest">
      {/* Top Navigation Bar */}
      <header className="flex justify-between items-center px-md py-sm w-full border-b border-outline-variant bg-surface z-50">
        <div className="flex items-center gap-sm">
          <img 
            alt="Logo" 
            className="w-10 h-10 rounded-full border border-primary-container p-0.5 object-cover bg-surface-container" 
            src="/logo.png"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface leading-tight">FundInsight</h1>
            <div className="flex items-center gap-xs">
              <span className={`w-2 h-2 rounded-full animate-pulse-green ${
                backendStatus === 'online' 
                  ? 'bg-primary-container' 
                  : backendStatus === 'checking'
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}></span>
              <span className="font-label-sm text-label-sm text-primary">
                {backendStatus === 'online' 
                  ? `Connected (${documentCount} facts)` 
                  : backendStatus === 'checking'
                  ? 'Connecting...'
                  : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-md">
          <span 
            onClick={() => setMessages([])}
            title="Clear Chat History"
            className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors select-none"
          >
            history
          </span>
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors select-none">
            account_balance
          </span>
        </div>
      </header>

      {/* Safety Banner / Offline Warning */}
      {backendStatus === 'offline' ? (
        <div className="w-full bg-red-950/20 px-md py-2 flex justify-between items-center border-b border-error/30 text-error">
          <p className="font-label-sm text-label-sm flex items-center gap-xs">
            <span className="material-symbols-outlined text-[16px]">wifi_off</span>
            Unable to establish live connection to facts assistant server.
          </p>
          <button 
            onClick={checkBackendHealth} 
            className="flex items-center gap-xs font-label-sm text-label-sm text-error underline hover:text-red-400 transition-colors"
          >
            <span className="material-symbols-outlined text-[14px]">refresh</span>
            Retry Connection
          </button>
        </div>
      ) : (
        <div className="w-full bg-surface-variant/30 px-md py-1.5 flex justify-center items-center border-b border-outline-variant">
          <p className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs">
            <span className="material-symbols-outlined text-[14px]">verified_user</span>
            Fact-checked AI Assistant. Verified against regulatory filings as of May 2024.
          </p>
        </div>
      )}

      {/* Main Chat Canvas */}
      <main className="flex-1 overflow-y-auto relative flex flex-col items-center">
        {messages.length === 0 ? (
          <WelcomeScreen onSelectQuery={handleSendMessage} />
        ) : (
          <div className="w-full max-w-3xl px-md py-lg space-y-lg pb-48" id="chat-stream">
            <ChatWindow messages={messages} isLoading={isLoading} />
          </div>
        )}
      </main>

      {/* Bottom Input Area */}
      <div className="fixed bottom-0 left-0 w-full bg-surface-container-lowest/80 backdrop-blur-md px-md pt-md pb-safe border-t border-outline-variant/10 z-40">
        <div className="max-w-3xl mx-auto flex flex-col gap-sm">
          <div className="flex items-center gap-sm bg-surface-container-low border border-outline-variant rounded-xl p-xs transition-all focus-within:border-primary-container focus-within:ring-1 focus-within:ring-primary-container/30 accent-glow-sm">
            <div className="pl-md flex items-center">
              <span className="material-symbols-outlined text-on-surface-variant select-none">search</span>
            </div>
            <input 
              className="w-full bg-transparent border-none text-on-surface placeholder:text-outline text-body-sm focus:ring-0 py-md px-sm outline-none" 
              placeholder="Ask about fund strategy, TER, exit load, or volatility..." 
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading || backendStatus === 'offline'}
            />
            <button 
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || isLoading || backendStatus === 'offline'}
              className="bg-primary-container text-on-primary-container p-md rounded-lg flex items-center justify-center hover:opacity-90 transition-opacity active:scale-95 transition-transform disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined select-none">send</span>
            </button>
          </div>

          {/* Footer Footnote */}
          <footer className="w-full py-md text-center flex flex-col items-center gap-xs opacity-60">
            <p className="font-label-sm text-label-sm text-outline">
              © 2026 FundInsight. Mutual fund investments are subject to market risks. Read all scheme related documents carefully before investing.
            </p>
            <div className="flex gap-md">
              <a className="font-label-sm text-label-sm text-outline hover:text-primary transition-colors" href="#">Terms</a>
              <a className="font-label-sm text-label-sm text-outline hover:text-primary transition-colors" href="#">Privacy</a>
              <a className="font-label-sm text-label-sm text-outline hover:text-primary transition-colors" href="#">Disclosures</a>
            </div>
          </footer>
        </div>
      </div>

      {/* Background Atmospheric Effect */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary/5 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-container/3 blur-[100px] rounded-full"></div>
      </div>
    </div>
  );
}
