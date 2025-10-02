from typing import Optional, Dict, List, Union
from pydantic import BaseModel
from enum import Enum
from uuid import UUID

class QuestionType(str, Enum):
    TEXT = "text"
    BUTTONS = "buttons"
    SCALE = "scale"
    DROPDOWN = "dropdown"
    MULTI_SELECT = "multi-select"
    RADIO = "radio"

class Question(BaseModel):
    id: int
    type: QuestionType
    question: str
    options: Optional[List[str]] = None
    min: Optional[int] = None
    max: Optional[int] = None

class TestRequest(BaseModel):
    user_id: UUID
    answer: Optional[Union[str, int, float, List[str]]] = None
    question_id: Optional[int] = None

class TestResponse(BaseModel):
    question: Optional[Question] = None
    completed: bool
    current_step: int
    total_score: Optional[float] = None
    message: str