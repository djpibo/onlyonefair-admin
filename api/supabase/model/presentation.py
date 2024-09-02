from typing import Optional

from pydantic import BaseModel

class ScreenDTO(BaseModel):
    peer_name: Optional[str]
    peer_company: Optional[str]
    comment: Optional[str]
    acc_score: Optional[float]
    used_score: Optional[float] = 0
    current_score: Optional[float] = 0
    enter_dvcd_kor: Optional[str] = None