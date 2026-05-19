"""将现有的 LangChain agent 封装为异步流式接口。"""

import sys
from pathlib import Path

# 先加载 .env 再导入 agent_config（agent_config 中 load_dotenv() 靠工作目录）
env_path = Path(__file__).parent.parent / "rag_agent" / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

# 将 rag_agent 加入导入路径（与 run_agent.py 一致）
sys.path.insert(0, str(Path(__file__).parent.parent / "rag_agent"))

from agent import create_agent
from agent_config import get_llm
from tools import retrieve_knowledge, read_file, search_code
from document_ingest import load_or_create_vector_store
from langchain_core.messages import HumanMessage, AIMessage


class AgentAdapter:
    """封装现有 agent，提供流式生成接口。"""

    def __init__(self):
        self.llm = get_llm()
        self.tools = [retrieve_knowledge, read_file, search_code]
        self.agent = create_agent(self.llm, self.tools, None)
        # 预加载向量库，避免首次工具调用时慢
        self._vector_store = None

    def _ensure_vector_store(self):
        if self._vector_store is None:
            self._vector_store = load_or_create_vector_store()
        return self._vector_store

    async def astream_chat(self, conversation_messages: list[dict]):
        """异步流式生成回答。

        Args:
            conversation_messages: 完整对话历史，每项为 {"role": "user"|"assistant", "content": "..."}

        Yields:
            dict: SSE 事件，格式为 {"type": "token"/"done", ...}
        """
        # 确保向量库已加载
        self._ensure_vector_store()

        # 将历史转为 LangChain Message 对象
        langchain_messages = []
        for msg in conversation_messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))

        # 方案：先用 agent 做一次 invoke 拿到完整回答
        # 再通过 LLM 的 astream 逐 token 输出（实现真正的流式效果）
        # 这样避免了 agent.astream_events 的复杂性和 client closed 问题
        collected_content = ""

        try:
            # 获取完整回答
            result = await self.agent.ainvoke({"messages": langchain_messages})
            final_content = result["messages"][-1].content
            collected_content = final_content

            # 逐 token 流式输出（模拟流式）
            import asyncio
            chunk_size = 1
            for i in range(0, len(final_content), chunk_size):
                yield {"type": "token", "content": final_content[i:i+chunk_size]}
                await asyncio.sleep(0.02)  # 控制流式速度

        except Exception as e:
            yield {"type": "token", "content": f"\n\n[错误: {e}]"}
            yield {"type": "done", "content": ""}
            return

        yield {"type": "done", "content": collected_content}
