"""对话记忆管理。"""

from langchain.memory import ConversationBufferMemory


def get_memory():
    """返回对话记忆实例。"""
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="input",
        output_key="output",
    )
