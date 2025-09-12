from typing import List, Optional, Literal, Union
from pydantic import BaseModel

class SendMessagePayload(BaseModel):
    recipient: str
    sender: str
    type: Literal["text", "media", "reaction", "notification"]
    body: Optional[Union[str, List[str]]] = None 
    subject: Optional[str] = None
    origin_msg_id: Optional[str] = None

class StatusPayload(BaseModel):
    type: Literal["read", "writing"]
    msg_id: str
    sender: str

class NormalizedEvent(BaseModel):
    recipient: Optional[str] = None
    sender: str
    message_id: Optional[str] = None
    timestamp: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    type: Optional[str] = None
    event_type: Optional[str] = None
    channel_type: str = "whatsapp"
    origin_msg_id: Optional[str] = None