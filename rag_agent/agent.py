"""Agent 执行器设置（LangChain 1.x LangGraph 风格）。"""

from dotenv import load_dotenv
from langchain.agents import create_agent as lc_create_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

load_dotenv()

SYSTEM_PROMPT = """你是一个代码和技术问答助手。你的工作是基于项目中的文档和代码文件回答用户的问题。

你可以使用以下工具：
1. retrieve_knowledge: 从项目文档库中检索相关信息。当需要回答关于项目代码、技术文档或指南的问题时，优先使用此工具。
2. read_file: 读取项目中的文件内容。当需要查看完整文件而非摘要时使用。
3. search_code: 在项目代码中搜索匹配的文本或代码模式。

工作流程：
1. 首先尝试用 retrieve_knowledge 工具检索相关信息
2. 如果需要查看更多细节，使用 read_file 工具读取完整文件
3. 如果检索不到相关信息，使用 search_code 工具搜索

注意事项：
- 始终用中文回答
- 如果找到相关信息，引用来源文件
- 如果找不到相关信息，诚实地说明"没有找到相关信息"
- 对于代码相关的问题，提供代码示例和分析
"""


def create_agent(
    llm: BaseLanguageModel,
    tools: list[BaseTool],
    memory,  # ConversationBufferMemory
):
    """创建 LangGraph 风格的 Agent。"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    # 使用 langchain.agents.create_agent (LangGraph 风格，已编译)
    return lc_create_agent(
        model=llm,
        tools=tools,
    )
