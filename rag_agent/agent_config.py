"""LLM 配置 - 支持 DeepSeek、Qwen 和自定义 OpenAI 兼容 API。"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 优先加载 rag_agent/.env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "deepseek")

    if provider == "deepseek":
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com/v1",
            temperature=0.3,
            max_tokens=4096,
        )
    elif provider == "qwen":
        return ChatOpenAI(
            model="qwen-plus",
            openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.3,
            max_tokens=4096,
        )
    elif provider == "custom":
        return ChatOpenAI(
            model=os.getenv("LLM_MODEL_NAME", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            temperature=0.3,
            max_tokens=4096,
        )
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")
