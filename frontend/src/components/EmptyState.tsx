export default function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-icon">💡</div>
      <h2>代码/技术问答助手</h2>
      <p>基于项目文档的智能问答</p>
      <div className="suggestions">
        <div className="suggestion-item">这个项目是做什么的？</div>
        <div className="suggestion-item">MCP 协议的架构是怎样的？</div>
        <div className="suggestion-item">gen_mcp_doc.py 的主要功能？</div>
        <div className="suggestion-item">什么是渐进式披露？</div>
      </div>
    </div>
  );
}
