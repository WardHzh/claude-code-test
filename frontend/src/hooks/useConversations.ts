import { useState, useCallback } from 'react';
import type { Conversation } from '../types';
import * as api from '../api/client';

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadConversations = useCallback(async () => {
    try {
      const list = await api.fetchConversations();
      setConversations(list);
    } catch (e) {
      console.error('加载对话列表失败', e);
    }
  }, []);

  const createConversation = useCallback(async () => {
    try {
      const conv = await api.createConversation();
      setConversations((prev) => [conv, ...prev]);
      setActiveId(conv.id);
      return conv;
    } catch (e) {
      console.error('创建对话失败', e);
      return null;
    }
  }, []);

  const deleteConv = useCallback(async (id: string) => {
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeId === id) {
        setActiveId(null);
      }
    } catch (e) {
      console.error('删除对话失败', e);
    }
  }, [activeId]);

  const renameConv = useCallback(async (id: string, title: string) => {
    try {
      await api.renameConversation(id, title);
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title } : c))
      );
    } catch (e) {
      console.error('重命名对话失败', e);
    }
  }, []);

  const selectConversation = useCallback((id: string | null) => {
    setActiveId(id);
  }, []);

  return {
    conversations,
    activeId,
    loading,
    loadConversations,
    createConversation,
    deleteConversation: deleteConv,
    renameConversation: renameConv,
    selectConversation,
  };
}
