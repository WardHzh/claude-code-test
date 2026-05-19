"""SSE 流式聊天端点。"""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.database import get_conversation, add_message, update_conversation_title
from backend.models import SendMessageRequest
from backend.adapters import AgentAdapter

router = APIRouter()

# 全局单例 adapter（agent 初始化较慢，复用）
_adapter: AgentAdapter | None = None


def get_adapter() -> AgentAdapter:
    global _adapter
    if _adapter is None:
        _adapter = AgentAdapter()
    return _adapter


@router.post("/conversations/{conv_id}/chat")
async def chat(conv_id: str, req: SendMessageRequest):
    """发送消息并以 SSE 流式返回回答。"""
    conv = get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 保存用户消息
    add_message(conv_id, "user", req.message)

    # 组装全部历史消息
    all_messages = conv["messages"] + [{"role": "user", "content": req.message}]

    # 自动生成标题：取用户第一条消息的前 20 个字
    if len(conv["messages"]) <= 1:
        title = req.message[:20].strip()
        if title:
            update_conversation_title(conv_id, title)

    adapter = get_adapter()

    async def event_stream():
        full_response = ""
        try:
            async for event in adapter.astream_chat(all_messages):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                if event["type"] == "token":
                    full_response += event["content"]
                elif event["type"] == "done":
                    full_response = event["content"]
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            # 保存完整回答
            if full_response:
                add_message(conv_id, "assistant", full_response)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
