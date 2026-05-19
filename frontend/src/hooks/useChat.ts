import { useState, useCallback, useRef } from 'react';
import type { Message, SSEEvent } from '../types';
import * as api from '../api/client';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef(false);

  const appendMessage = useCallback((msg: Message) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const loadMessages = useCallback((msgs: Message[]) => {
    setMessages(msgs);
  }, []);

  const sendMessage = useCallback(async (conversationId: string, content: string) => {
    if (isStreaming) return;
    abortRef.current = false;

    // 添加用户消息
    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setStreamingContent('');

    let fullContent = '';

    try {
      await api.sendChatMessage(conversationId, content, (event: SSEEvent) => {
        if (abortRef.current) return;

        switch (event.type) {
          case 'token':
            fullContent += event.content || '';
            setStreamingContent(fullContent);
            break;
          case 'done':
            // 完成，将流式内容转为正式消息
            const aiMsg: Message = {
              id: Date.now() + 1,
              role: 'assistant',
              content: event.content || fullContent,
              created_at: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, aiMsg]);
            setStreamingContent('');
            setIsStreaming(false);
            break;
          case 'error':
            console.error('SSE error:', event.content);
            setIsStreaming(false);
            break;
        }
      });
    } catch (e) {
      console.error('发送消息失败', e);
      setIsStreaming(false);
      setStreamingContent('');
    }
  }, [isStreaming]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setStreamingContent('');
    setIsStreaming(false);
  }, []);

  return {
    messages,
    streamingContent,
    isStreaming,
    appendMessage,
    loadMessages,
    sendMessage,
    clearMessages,
  };
}
