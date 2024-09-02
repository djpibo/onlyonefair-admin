from typing import Optional

from pydantic import BaseModel
from datetime import datetime

class CommonCodeDTO(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    cmn_nm: str
    cmn_cd: str
    cmn_desc: str

    class Config:
        from_attributes = True

class LoginDTO(BaseModel):
    peer_id: int
    argv_company_dvcd: int
    peer_name: Optional[str] = None
    peer_company: Optional[str] = None
    enter_dvcd: Optional[int] = None

    class Config:
        from_attributes = True