import { useEffect, useCallback } from 'react';
import Layout from './components/Layout';
import Sidebar from './components/Sidebar';
import ChatView from './components/ChatView';
import InputBar from './components/InputBar';
import { useConversations } from './hooks/useConversations';
import { useChat } from './hooks/useChat';
import { getConversation } from './api/client';

export default function App() {
  const {
    conversations,
    activeId,
    loadConversations,
    createConversation,
    deleteConversation,
    renameConversation,
    selectConversation,
  } = useConversations();

  const {
    messages,
    streamingContent,
    isStreaming,
    loadMessages,
    sendMessage,
    clearMessages,
  } = useChat();

  // 加载对话列表
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // 切换对话时加载消息
  useEffect(() => {
    if (activeId) {
      getConversation(activeId)
        .then((conv) => {
          loadMessages(conv.messages || []);
        })
        .catch(console.error);
    } else {
      clearMessages();
    }
  }, [activeId, loadMessages, clearMessages]);

  const handleNewConversation = useCallback(async () => {
    const conv = await createConversation();
    if (conv) {
      clearMessages();
    }
  }, [createConversation, clearMessages]);

  const handleSelectConversation = useCallback((id: string) => {
    selectConversation(id);
  }, [selectConversation]);

  const handleSend = useCallback((message: string) => {
    if (activeId) {
      sendMessage(activeId, message);
    }
  }, [activeId, sendMessage]);

  const handleDelete = useCallback((id: string) => {
    if (id === activeId) {
      clearMessages();
    }
    deleteConversation(id);
  }, [activeId, clearMessages, deleteConversation]);

  return (
    <Layout
      sidebar={
        <Sidebar
          conversations={conversations}
          activeId={activeId}
          onSelect={handleSelectConversation}
          onNew={handleNewConversation}
          onDelete={handleDelete}
          onRename={renameConversation}
        />
      }
    >
      <ChatView
        messages={messages}
        streamingContent={streamingContent}
        isStreaming={isStreaming}
      />
      {activeId && (
        <InputBar onSend={handleSend} disabled={isStreaming} />
      )}
      {!activeId && (
        <div className="no-conversation-hint">
          请在左侧创建一个新对话
        </div>
      )}
    </Layout>
  );
}
