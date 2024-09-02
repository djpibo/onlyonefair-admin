from typing import Optional

from pydantic import BaseModel
from datetime import datetime

class PeerInfoDTO(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    company: str
    name: str
    nfc_id: str
    grade: Optional[int] = 0

    class Config:
        from_attributes = True

class ConsumeInfoDTO(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    seqno: Optional[int] = None
    consume_dvcd: int
    used_score: float
    cancel_yn: Optional[bool] = False

    class Config:
        from_attributes = True

class OliveInfoDTO(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    seqno: Optional[int] = None
    count: Optional[int]
    used_count: Optional[int]

    class Config:
        from_attributes = True