"""文档加载、中文分割、嵌入和 FAISS 索引。"""

import os
from pathlib import Path

# 中国网络环境：使用 HuggingFace 镜像站
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, Docx2txtLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {".md", ".py", ".txt", ".rst", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini"}
# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", ".claude", "vector_store", "rag_agent", "venv_agent"}

# 中文感知的分隔符（按语义单位从大到小排列）
CHINESE_SEPARATORS = [
    "\n\n",
    "\n",
    "。",
    "！",
    "？",
    "；",
    "，",
    "、",
    " ",
    "",
]

VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store/faiss_index")
DOCUMENTS_ROOT = os.getenv("DOCUMENTS_ROOT", "./../")


def get_loader(file_path: Path):
    """根据文件扩展名返回对应的加载器。"""
    suffix = file_path.suffix.lower()
    if suffix == ".docx":
        return Docx2txtLoader(str(file_path))
    else:
        return TextLoader(str(file_path), encoding="utf-8")


def load_documents(root_dir: str) -> list[Document]:
    """递归加载所有支持的文档。"""
    root = Path(root_dir).resolve()
    docs = []

    for file_path in root.rglob("*"):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if file_path.is_dir():
            continue
        if any(skip in file_path.parts for skip in SKIP_DIRS):
            continue

        try:
            loader = get_loader(file_path)
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source"] = str(file_path.relative_to(root))
            docs.extend(loaded)
        except Exception as e:
            print(f"  跳过 {file_path}: {e}")

    return docs


def get_text_splitter():
    """返回中文感知的文本分割器。"""
    return RecursiveCharacterTextSplitter(
        separators=CHINESE_SEPARATORS,
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )


def get_embeddings():
    """返回中文嵌入模型。"""
    model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-zh-v1.5")
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_or_create_vector_store() -> FAISS:
    """加载已有索引，或创建新的索引。"""
    embeddings = get_embeddings()
    store_path = Path(VECTOR_STORE_PATH)

    if store_path.exists():
        print(f"  加载已有索引: {store_path}")
        return FAISS.load_local(
            str(store_path), embeddings, allow_dangerous_deserialization=True
        )

    print("  正在加载文档...")
    docs = load_documents(DOCUMENTS_ROOT)
    print(f"  加载了 {len(docs)} 个文档")

    print("  正在分割文档...")
    text_splitter = get_text_splitter()
    chunks = text_splitter.split_documents(docs)
    print(f"  分割为 {len(chunks)} 个文本块")

    print("  正在创建向量索引...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    print(f"  保存索引到 {store_path}...")
    store_path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(store_path))

    return vector_store


def update_index():
    """增量更新索引（检查文件修改时间）。"""
    embeddings = get_embeddings()
    store_path = Path(VECTOR_STORE_PATH)

    if not store_path.exists():
        print("  索引不存在，创建新索引...")
        return load_or_create_vector_store()

    vector_store = FAISS.load_local(
        str(store_path), embeddings, allow_dangerous_deserialization=True
    )

    docs = load_documents(DOCUMENTS_ROOT)
    text_splitter = get_text_splitter()
    chunks = text_splitter.split_documents(docs)

    vector_store.add_documents(chunks)
    vector_store.save_local(str(store_path))
    print(f"  索引已更新，共 {vector_store.index.ntotal} 个向量")

    return vector_store
