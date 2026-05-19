"""主入口：CLI 交互循环。"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# 将项目根目录加入 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from agent import create_agent
from agent_config import get_llm
from document_ingest import load_or_create_vector_store
from tools import retrieve_knowledge, read_file, search_code

load_dotenv()


def main():
    print("=" * 60)
    print("  LangChain 代码/技术问答助手")
    print("=" * 60)

    # 1. 加载或创建向量索引
    print("\n[1/3] 正在加载文档索引...")
    try:
        vector_store = load_or_create_vector_store()
        print(f"  ✓ 索引就绪")
    except Exception as e:
        print(f"  ✗ 索引加载失败: {e}")
        print("  请确保已配置 API Key 并安装了依赖。")
        return

    # 2. 初始化 LLM
    print("\n[2/3] 正在初始化语言模型...")
    try:
        llm = get_llm()
        print(f"  ✓ LLM 就绪")
    except Exception as e:
        print(f"  ✗ LLM 初始化失败: {e}")
        print("  请检查 .env 文件中的 API Key 配置。")
        return

    # 3. 创建 Agent（LangGraph 风格，不使用 AgentExecutor）
    print("\n[3/3] 正在创建 Agent...")
    tools = [retrieve_knowledge, read_file, search_code]
    agent = create_agent(llm, tools, None)
    print("  ✓ Agent 就绪")

    # 4. CLI 交互循环
    print("\n" + "=" * 60)
    print("  代码/技术问答助手已启动")
    print("  输入 'exit' 或 'quit' 或 '退出' 退出")
    print("=" * 60)

    # 手动维护对话历史
    messages = []

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n再见！")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "退出"):
            print("再见！")
            break

        print("\n助手: ", end="", flush=True)
        try:
            messages.append(HumanMessage(content=user_input))
            response = agent.invoke({
                "messages": messages,
            })
            # 提取 AI 回复并加入历史
            ai_msg = response["messages"][-1]
            messages.append(ai_msg)
            print(ai_msg.content)
        except Exception as e:
            print(f"处理请求时出错: {e}")


if __name__ == "__main__":
    main()
