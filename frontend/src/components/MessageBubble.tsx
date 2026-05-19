import type { Message } from '../types';

interface Props {
  message: Message;
  isStreaming?: boolean;
}

export default function MessageBubble({ message, isStreaming }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="avatar">
        {isUser ? '我' : 'AI'}
      </div>
      <div className="bubble">
        <div className="content">
          {message.content}
          {isStreaming && <span className="cursor">▊</span>}
        </div>
      </div>
    </div>
  );
}
