"""RAG 检索链。"""

from langchain_community.vectorstores import FAISS
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


def create_rag_chain(
    llm: BaseLanguageModel,
    vector_store: FAISS,
):
    """创建 RAG 检索链。

    从向量库检索相关文档，结合 LLM 生成回答。
    """
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )

    template = """你是一个代码和技术问答助手。请基于提供的上下文信息回答用户的问题。

上下文信息：
{context}

历史对话：
{chat_history}

用户问题：{input}

请用中文回答。回答要求：
1. 如果上下文信息足够，给出清晰准确的回答
2. 如果上下文信息不足以回答问题，请明确说明"根据现有文档无法确定"
3. 如果问题涉及代码，提供具体的代码示例和分析
4. 引用信息来源文件（在上下文中有"[来源: xxx]"标记）
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain, retriever
