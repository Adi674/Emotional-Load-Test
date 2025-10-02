from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP
from datetime import datetime
from config.database import Base

class QuestionBankModel(Base):
    """Stores all test questions"""
    __tablename__ = "question_bank"
    
    id = Column(Integer, primary_key=True)
    step_number = Column(Integer, unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)
    min = Column(Integer, nullable=True)
    max = Column(Integer, nullable=True)
    scores = Column(JSONB, nullable=True)
    is_active = Column(SmallInteger, default=1, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class UserProgressModel(Base):
    """Stores user progress and answers"""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('public.users.user_id', ondelete='CASCADE', onupdate='CASCADE'),  # ✅ Added 'public.'
        unique=True,
        nullable=False,
        index=True
    )
    current_step = Column(Integer, default=1)
    answers = Column(JSONB, default=list)
    total_score = Column(Float, default=0.0)
    is_completed = Column(SmallInteger, default=0, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)