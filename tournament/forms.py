from pydantic import BaseModel, Field
from datetime import date
from typing import List


class TournamentCreateForm(BaseModel):
    name: str


class CompetitorCreateForm(BaseModel):
    name: str


class CompetitorListForm(BaseModel):
    competitor_ids: List[int]


class MatchResultRequest(BaseModel):
    winner_id: int
