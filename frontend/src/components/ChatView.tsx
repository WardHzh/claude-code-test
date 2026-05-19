import { useEffect, useRef } from 'react';
import type { Message } from '../types';
import MessageBubble from './MessageBubble';
import EmptyState from './EmptyState';

interface Props {
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
}

export default function ChatView({ messages, streamingContent, isStreaming }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isStreaming) {
    return <EmptyState />;
  }

  return (
    <div className="chat-view">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {isStreaming && streamingContent && (
        <MessageBubble
          message={{
            id: 0,
            role: 'assistant',
            content: streamingContent,
            created_at: new Date().toISOString(),
          }}
          isStreaming
        />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
