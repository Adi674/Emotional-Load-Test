from typing import Union, List
from uuid import UUID  # ✅ Add this
from sqlalchemy.orm import Session  # ✅ Add this
from models.database import QuestionBankModel
from models.schemas import QuestionType

class ScoringService:
    """Async scoring service - pure computation"""
    
    @staticmethod
    async def calculate(
        question_db: QuestionBankModel, 
        answer_value: Union[str, int, float, List[str]]
    ) -> float:
        """
        Async wrapper for score calculation
        Pure computation - no I/O, but async for consistency
        """
        if not question_db.scores:
            return 0.0
        
        calculators = {
            QuestionType.SCALE: ScoringService._calculate_scale,
            QuestionType.MULTI_SELECT: ScoringService._calculate_multi_select,
            QuestionType.BUTTONS: ScoringService._calculate_single_choice,
            QuestionType.RADIO: ScoringService._calculate_single_choice,
            QuestionType.DROPDOWN: ScoringService._calculate_single_choice,
            QuestionType.TEXT: ScoringService._calculate_text,
        }
        
        calculator = calculators.get(question_db.type, ScoringService._calculate_default)
        return calculator(question_db, answer_value)
    
    @staticmethod
    def _calculate_scale(question_db: QuestionBankModel, value: Union[int, float]) -> float:
        """Scale: value is the score"""
        return float(value)
    
    @staticmethod
    def _calculate_multi_select(question_db: QuestionBankModel, values: List[str]) -> float:
        """Multi-select: sum all selected options"""
        if not isinstance(values, list):
            return 0.0
        
        total = 0.0
        for option in values:
            total += question_db.scores.get(option, 0)
        return total
    
    @staticmethod
    def _calculate_single_choice(question_db: QuestionBankModel, value: str) -> float:
        """Single choice: get score of selected option"""
        return question_db.scores.get(str(value), 0)
    
    @staticmethod
    def _calculate_text(question_db: QuestionBankModel, value: str) -> float:
        """Text: no scoring by default"""
        return 0.0
    
    @staticmethod
    def _calculate_default(question_db: QuestionBankModel, value: any) -> float:
        """Default: no score"""
        return 0.0
    
    @staticmethod
    async def calculate_total_score(db: Session, user_id: UUID) -> float:
        """Calculate total score from all answers"""
        from models.database import UserProgressModel
        
        progress = db.query(UserProgressModel).filter(
            UserProgressModel.user_id == user_id
        ).first()
        
        return progress.total_score if progress else 0.0