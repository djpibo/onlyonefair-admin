from typing import Optional

from pydantic import BaseModel
from datetime import datetime

class EntranceInfoDTO(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    enter_dvcd: int
    company_dvcd: int
    seqno: int
    exit_yn: bool

    class Config:
        from_attributes = True

class CountInfoDTO(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    seqno: Optional[int] = None

    class Config:
        from_attributes = True