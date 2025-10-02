from sqlalchemy.orm import Session
from datetime import datetime
from typing import Union, List, Optional
from uuid import UUID
from models.database import UserProgressModel, QuestionBankModel
from services.scoring_service import ScoringService

class ProgressService:
    """Async service for user progress management"""
    
    @staticmethod
    async def get_or_create(db: Session, user_id: UUID) -> UserProgressModel:
        """Get existing progress or create new one"""
        progress = db.query(UserProgressModel).filter(
            UserProgressModel.user_id == user_id
        ).first()
        
        if not progress:
            progress = UserProgressModel(
                user_id=user_id,
                current_step=1,
                answers=[],
                total_score=0.0
            )
            db.add(progress)
            db.commit()
            db.refresh(progress)
        
        return progress
    
    @staticmethod
    async def save_answer(
        db: Session,
        progress: UserProgressModel,
        question_db: QuestionBankModel,
        answer_value: Union[str, int, float, List[str]]
    ) -> float:
        """Save answer and calculate score"""
        
        # Calculate score (async)
        score = await ScoringService.calculate(question_db, answer_value)
        
        # Update total score
        progress.total_score += score
        
        # Save answer
        answers = progress.answers or []
        answers.append({
            "question_id": question_db.id,
            "step": progress.current_step,
            "value": answer_value,
            "score": score
        })
        progress.answers = answers
        progress.updated_at = datetime.utcnow()
        
        db.commit()
        return score
    
    @staticmethod
    async def move_to_next_step(db: Session, progress: UserProgressModel):
        """Move user to next step"""
        progress.current_step += 1
        db.commit()
    
    @staticmethod
    async def mark_completed(db: Session, progress: UserProgressModel):
        """Mark test as completed"""
        progress.is_completed = 1
        db.commit()
    
    @staticmethod
    async def get_progress(db: Session, user_id: UUID) -> Optional[UserProgressModel]:
        """Get user progress by ID"""
        return db.query(UserProgressModel).filter(
            UserProgressModel.user_id == user_id
        ).first()
    
    @staticmethod
    async def reset_progress(db: Session, user_id: UUID) -> bool:
        """Reset user progress (start over)"""
        progress = db.query(UserProgressModel).filter(
            UserProgressModel.user_id == user_id
        ).first()
        
        if not progress:
            return False
        
        progress.current_step = 1
        progress.answers = []
        progress.total_score = 0.0
        progress.is_completed = 0
        progress.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    
    @staticmethod
    async def delete_progress(db: Session, user_id: UUID) -> bool:
        """Delete user progress completely"""
        progress = db.query(UserProgressModel).filter(
            UserProgressModel.user_id == user_id
        ).first()
        
        if not progress:
            return False
        
        db.delete(progress)
        db.commit()
        return True