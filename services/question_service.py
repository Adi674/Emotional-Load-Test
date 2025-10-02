from sqlalchemy.orm import Session
from typing import Optional
from models.database import QuestionBankModel
from models.schemas import Question

class QuestionService:
    """Async service with sync database operations"""
    
    @staticmethod
    async def get_by_step(db: Session, step: int) -> Optional[Question]:
        """
        Async function with sync DB query
        Database operations are fast, so sync is fine
        """
        db_question = db.query(QuestionBankModel).filter(
            QuestionBankModel.step_number == step,
            QuestionBankModel.is_active == 1
        ).first()
        
        if not db_question:
            return None
        
        # Transform to Pydantic model (async processing)
        return Question(
            id=db_question.id,
            type=db_question.type,
            question=db_question.question,
            options=db_question.options,
            min=db_question.min,
            max=db_question.max
        )
    
    @staticmethod
    async def get_by_step_with_scores(db: Session, step: int) -> Optional[QuestionBankModel]:
        """Get question with scores for backend processing"""
        return db.query(QuestionBankModel).filter(
            QuestionBankModel.step_number == step,
            QuestionBankModel.is_active == 1
        ).first()
    
    @staticmethod
    async def get_all_active_questions(db: Session) -> list[QuestionBankModel]:
        """Get all active questions (for admin/reporting)"""
        return db.query(QuestionBankModel).filter(
            QuestionBankModel.is_active == 1
        ).order_by(QuestionBankModel.step_number).all()
    
    @staticmethod
    async def get_total_questions(db: Session) -> int:
        """Get total number of active questions"""
        return db.query(QuestionBankModel).filter(
            QuestionBankModel.is_active == 1
        ).count()