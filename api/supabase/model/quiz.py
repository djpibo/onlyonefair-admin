from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ScoreInfoDTO(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    quiz_dvcd: int
    company_dvcd: int
    score: float

    class Config:
        from_attributes = True

class RankDTO(BaseModel):
    id: int
    total_score: Optional[float]
    rank: Optional[int]
    name: Optional[str]
    company: Optional[str]
    room_score: Optional[float]
    quiz_score: Optional[float]
    photo_score: Optional[float]
    survey_score: Optional[float]

    class Config:
        from_attributes = True