import React, { useEffect, useRef } from 'react';

export default function ChatWindow({ messages, isLoading }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // A basic helper to render markdown tables and markdown links in answers safely
  const renderMessageContent = (text) => {
    if (!text) return "";

    const parts = [];
    const lines = text.split('\n');
    let currentTextBlock = [];
    let currentTableBlock = [];
    let inTable = false;

    lines.forEach((line) => {
      const isTableLine = line.trim().startsWith('|') && line.trim().endsWith('|');
      
      if (isTableLine) {
        if (!inTable) {
          if (currentTextBlock.length > 0) {
            parts.push({ type: 'text', content: currentTextBlock.join('\n') });
            currentTextBlock = [];
          }
          inTable = true;
        }
        currentTableBlock.push(line);
      } else {
        if (inTable) {
          if (currentTableBlock.length > 0) {
            parts.push({ type: 'table', content: currentTableBlock.join('\n') });
            currentTableBlock = [];
          }
          inTable = false;
        }
        currentTextBlock.push(line);
      }
    });

    if (inTable && currentTableBlock.length > 0) {
      parts.push({ type: 'table', content: currentTableBlock.join('\n') });
    } else if (currentTextBlock.length > 0) {
      parts.push({ type: 'text', content: currentTextBlock.join('\n') });
    }

    return parts.map((part, index) => {
      if (part.type === 'table') {
        return parseMarkdownTable(part.content, index);
      } else {
        return parseMarkdownText(part.content, index);
      }
    });
  };

  const parseMarkdownText = (textBlock, blockIdx) => {
    const paragraphs = textBlock.split('\n\n').filter(p => p.trim());
    
    return paragraphs.map((p, pIdx) => {
      const linkRegex = /\[(.*?)\]\((.*?)\)/g;
      let match;
      let lastIndex = 0;
      const elements = [];

      while ((match = linkRegex.exec(p)) !== null) {
        const textBefore = p.substring(lastIndex, match.index);
        const [fullMatch, label, url] = match;
        
        if (textBefore) {
          elements.push(textBefore);
        }
        
        elements.push(
          <a 
            key={match.index} 
            href={url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-primary font-medium underline underline-offset-4 decoration-primary/30 hover:text-primary-fixed-dim"
          >
            {label}
          </a>
        );
        
        lastIndex = linkRegex.lastIndex;
      }

      if (lastIndex < p.length) {
        elements.push(p.substring(lastIndex));
      }

      const isLastUpdated = p.trim().startsWith('Last updated from sources:');
      
      return (
        <p 
          key={`${blockIdx}-${pIdx}`} 
          className={`font-body-sm text-on-surface leading-relaxed ${
            isLastUpdated ? "border-t border-outline-variant/30 mt-md pt-sm text-xs opacity-60 font-label-sm" : ""
          }`}
        >
          {elements.length > 0 ? elements : p}
        </p>
      );
    });
  };

  const parseMarkdownTable = (tableMarkdown, idx) => {
    const rows = tableMarkdown.split('\n').map(row => 
      row.trim().split('|').map(cell => cell.trim()).filter((_, i, arr) => i > 0 && i < arr.length - 1)
    ).filter(row => row.length > 0);

    if (rows.length < 2) return null;

    const headers = rows[0];
    const dataRows = rows.slice(2);

    return (
      <div key={`table-${idx}`} className="overflow-x-auto w-full my-md border border-outline-variant/30 rounded-lg">
        <table className="min-w-full divide-y divide-outline-variant/30 text-left text-body-sm">
          <thead className="bg-surface-container-high/50 text-primary font-semibold">
            <tr>
              {headers.map((h, i) => (
                <th key={i} className="px-md py-sm border-b border-outline-variant/30">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/30 bg-surface-container/20">
            {dataRows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-surface-container-high/30 transition-colors">
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-md py-sm text-on-surface-variant font-normal">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="w-full space-y-lg flex flex-col">
      {messages.map((msg, index) => {
        const isBot = msg.sender === 'bot';
        
        if (!isBot) {
          // User message bubble
          return (
            <div key={index} className="flex justify-end w-full">
              <div className="max-w-[80%] bg-surface-container-high border border-outline-variant px-md py-sm rounded-xl rounded-tr-none">
                <p className="font-body-sm text-on-surface">{msg.text}</p>
              </div>
            </div>
          );
        }

        // Bot message bubble
        return (
          <div key={index} className="flex justify-start w-full">
            <div className={`max-w-[90%] glass-card p-lg rounded-xl rounded-tl-none accent-glow-sm w-full ${
              msg.refused ? 'border-error/40 bg-error-container/10' : ''
            }`}>
              <div className="flex items-center gap-xs mb-md">
                <span 
                  className={`material-symbols-outlined text-[18px] ${msg.refused ? 'text-error' : 'text-primary'}`} 
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  {msg.refused ? 'report' : 'auto_awesome'}
                </span>
                <span className={`font-label-md text-label-md uppercase tracking-widest ${
                  msg.refused ? 'text-error' : 'text-primary'
                }`}>
                  {msg.refused ? 'Guardrail Notice' : 'Fact Insight AI'}
                </span>
              </div>
              <div className="space-y-md">
                {renderMessageContent(msg.text)}
                
                {msg.citation && !msg.refused && (
                  <div className="flex gap-sm pt-sm">
                    <a 
                      href={msg.citation} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="px-sm py-1.5 rounded bg-outline-variant/20 border border-outline-variant/50 text-label-sm font-label-sm hover:bg-outline-variant/40 hover:text-primary transition-colors flex items-center gap-xs"
                    >
                      <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                      <span>View Reference Sheet</span>
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
      
      {isLoading && (
        <div className="flex justify-start w-full">
          <div className="max-w-[90%] glass-card p-lg rounded-xl rounded-tl-none accent-glow-sm w-full animate-pulse">
            <div className="flex items-center gap-xs mb-md">
              <span 
                className="material-symbols-outlined text-primary text-[18px] animate-spin" 
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                progress_activity
              </span>
              <span className="font-label-md text-label-md text-primary uppercase tracking-widest">
                Fact Insight AI is retrieving details...
              </span>
            </div>
            <div className="space-y-sm">
              <div className="h-3 bg-surface-container-high rounded w-3/4"></div>
              <div className="h-3 bg-surface-container-high rounded w-5/6"></div>
              <div className="h-3 bg-surface-container-high rounded w-1/2"></div>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
}
