"""自定义工具定义。"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store/faiss_index")
DOCUMENTS_ROOT = Path(os.getenv("DOCUMENTS_ROOT", "./../")).resolve()

SKIP_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", ".claude", "vector_store", "venv_agent"}


def _get_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-zh-v1.5"),
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return FAISS.load_local(
        str(VECTOR_STORE_PATH), embeddings, allow_dangerous_deserialization=True
    )


@tool
def retrieve_knowledge(query: str) -> str:
    """基于查询从项目文档中检索相关信息。当需要回答关于项目代码、技术文档或指南的问题时使用此工具。

Args:
    query: 中文自然语言问题
    """
    try:
        vector_store = _get_vector_store()
        docs = vector_store.similarity_search(query, k=4)
        if not docs:
            return "未找到相关文档信息。"
        results = []
        for doc in docs:
            source = doc.metadata.get("source", "未知来源")
            results.append(f"[来源: {source}]\n{doc.page_content}")
        return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"检索出错: {e}"


@tool
def read_file(file_path: str) -> str:
    """读取项目中的文件内容。当需要查看完整文件而非摘要时使用。

Args:
    file_path: 文件路径，相对于项目根目录或绝对路径
    """
    try:
        path = Path(file_path)
        if not path.is_absolute():
            path = DOCUMENTS_ROOT / path

        path = path.resolve()

        if not str(path).startswith(str(DOCUMENTS_ROOT)):
            return "错误：不允许读取项目目录之外的文件。"

        if not path.exists():
            return f"文件不存在: {file_path}"

        if path.is_dir():
            return f"路径是一个目录，不是文件: {file_path}"

        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > 8000:
            content = content[:8000] + "\n\n... (文件过长，已截断)"
        return content
    except Exception as e:
        return f"读取文件出错: {e}"


@tool
def search_code(pattern: str) -> str:
    """在项目代码中搜索匹配的文本或代码模式。

Args:
    pattern: 搜索关键词或正则表达式
    """
    try:
        results = []
        matched_files = set()

        for file_path in DOCUMENTS_ROOT.rglob("*"):
            if file_path.is_dir():
                continue
            if any(skip in file_path.parts for skip in SKIP_DIRS):
                continue

            suffix = file_path.suffix.lower()
            if suffix not in {".md", ".py", ".txt", ".rst", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini", ".docx"}:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        rel_path = file_path.relative_to(DOCUMENTS_ROOT)
                        line = line.strip()[:120]
                        results.append(f"{rel_path}:{i}  {line}")
                        matched_files.add(str(rel_path))
                        if len(results) >= 30:
                            break
            except Exception:
                continue
            if len(results) >= 30:
                break

        if not results:
            return f"未找到匹配 '{pattern}' 的代码。"

        summary = f"在 {len(matched_files)} 个文件中找到 {len(results)} 处匹配:\n\n"
        return summary + "\n".join(results)
    except Exception as e:
        return f"搜索代码出错: {e}"
