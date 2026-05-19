from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    title: str = "新对话"


class RenameConversationRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    message: str
