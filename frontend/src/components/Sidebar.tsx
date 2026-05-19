import type { Conversation } from '../types';

interface Props {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  onRename: (id: string, title: string) => void;
}

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onRename,
}: Props) {
  return (
    <div className="sidebar">
      <button className="new-chat-button" onClick={onNew}>
        <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
          <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        新对话
      </button>

      <div className="conversation-list">
        {conversations.length === 0 && (
          <div className="no-conversations">暂无对话</div>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`conversation-item ${activeId === conv.id ? 'active' : ''}`}
            onClick={() => onSelect(conv.id)}
          >
            <div className="conv-title">{conv.title}</div>
            <div className="conv-actions">
              <button
                className="conv-action-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  const newTitle = prompt('重命名对话:', conv.title);
                  if (newTitle && newTitle.trim()) {
                    onRename(conv.id, newTitle.trim());
                  }
                }}
                title="重命名"
              >
                ✏️
              </button>
              <button
                className="conv-action-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm('确定删除此对话？')) {
                    onDelete(conv.id);
                  }
                }}
                title="删除"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
