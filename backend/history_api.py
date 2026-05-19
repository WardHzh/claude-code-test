"""对话历史 CRUD 端点。"""

from fastapi import APIRouter, HTTPException

from backend.database import (
    list_conversations,
    create_conversation,
    get_conversation,
    delete_conversation,
    rename_conversation,
)
from backend.models import CreateConversationRequest, RenameConversationRequest

router = APIRouter()


@router.get("/conversations")
async def api_list_conversations():
    """获取所有对话列表（不含消息内容）。"""
    return list_conversations()


@router.post("/conversations")
async def api_create_conversation(req: CreateConversationRequest):
    """创建新对话。"""
    return create_conversation(req.title)


@router.get("/conversations/{conv_id}")
async def api_get_conversation(conv_id: str):
    """获取单个对话详情（含所有消息）。"""
    conv = get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conv


@router.delete("/conversations/{conv_id}")
async def api_delete_conversation(conv_id: str):
    """删除对话。"""
    if not delete_conversation(conv_id):
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"ok": True}


@router.patch("/conversations/{conv_id}")
async def api_rename_conversation(conv_id: str, req: RenameConversationRequest):
    """重命名对话。"""
    if not rename_conversation(conv_id, req.title):
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"ok": True}
