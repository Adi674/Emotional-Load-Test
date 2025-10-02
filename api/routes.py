from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from config.database import get_db
from models.database import UserProgressModel
from models.schemas import TestRequest, TestResponse, Question
from services.question_service import QuestionService
from services.progress_service import ProgressService
from services.scoring_service import ScoringService

router = APIRouter(prefix="/api/test", tags=["emotional-test"])


@router.post("/process", response_model=TestResponse)
async def process_test(request: TestRequest, db: Session = Depends(get_db)):
    """
    Main endpoint for test flow
    Async endpoint with sync database
    """
    try:
        # Get or create user progress
        progress = await ProgressService.get_or_create(db, request.user_id)
        
        # Check if already completed
        if progress.is_completed:
            return TestResponse(
                question=None,
                completed=True,
                current_step=progress.current_step,
                total_score=progress.total_score,
                message="Test already completed!"
            )
        
        # If answer provided, save it
        if request.answer is not None and request.question_id is not None:
            # Get question with scores
            current_question_db = await QuestionService.get_by_step_with_scores(
                db, progress.current_step
            )
            
            if not current_question_db:
                raise HTTPException(status_code=400, detail="Invalid question")
            
            # Save answer
            await ProgressService.save_answer(db, progress, current_question_db, request.answer)
            
            # Move to next step
            await ProgressService.move_to_next_step(db, progress)
        
        # Get next question
        next_question = await QuestionService.get_by_step(db, progress.current_step)
        
        if next_question:
            return TestResponse(
                question=next_question,
                completed=False,
                current_step=progress.current_step,
                total_score=None,
                message="Next question"
            )
        
        # No more questions - mark completed
        await ProgressService.mark_completed(db, progress)
        
        return TestResponse(
            question=None,
            completed=True,
            current_step=progress.current_step,
            total_score=progress.total_score,
            message="Test completed successfully!"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{user_id}")
async def get_progress(user_id: str, db: Session = Depends(get_db)):
    """Get user's current progress"""
    
    progress = await ProgressService.get_progress(db, UUID(user_id))
    
    if not progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    return {
        "user_id": str(progress.user_id),
        "current_step": progress.current_step,
        "total_score": progress.total_score,
        "is_completed": bool(progress.is_completed),
        "answers": progress.answers,
        "created_at": progress.created_at,
        "updated_at": progress.updated_at
    }


@router.post("/reset/{user_id}")
async def reset_progress(user_id: str, db: Session = Depends(get_db)):
    """Reset user progress to start over"""
    
    success = await ProgressService.reset_progress(db, UUID(user_id))
    
    if not success:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    return {"message": "Progress reset successfully"}


@router.delete("/progress/{user_id}")
async def delete_progress(user_id: str, db: Session = Depends(get_db)):
    """Delete user progress completely"""
    
    success = await ProgressService.delete_progress(db, UUID(user_id))
    
    if not success:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    return {"message": "Progress deleted successfully"}


@router.get("/questions", response_model=List[Question])
async def get_all_questions(db: Session = Depends(get_db)):
    """Get all active questions (admin endpoint)"""
    
    questions = await QuestionService.get_all_active_questions(db)
    
    return [
        Question(
            id=q.id,
            type=q.type,
            question=q.question,
            options=q.options,
            min=q.min,
            max=q.max
        )
        for q in questions
    ]


@router.get("/stats")
async def get_test_stats(db: Session = Depends(get_db)):
    """Get overall test statistics"""
    
    total_questions = await QuestionService.get_total_questions(db)
    
    total_users = db.query(UserProgressModel).count()
    completed_users = db.query(UserProgressModel).filter(
        UserProgressModel.is_completed == 1
    ).count()
    
    avg_score = db.query(UserProgressModel).filter(
        UserProgressModel.is_completed == 1
    ).with_entities(
        db.func.avg(UserProgressModel.total_score)
    ).scalar() or 0.0
    
    return {
        "total_questions": total_questions,
        "total_users": total_users,
        "completed_users": completed_users,
        "completion_rate": f"{(completed_users / total_users * 100):.2f}%" if total_users > 0 else "0%",
        "average_score": round(avg_score, 2)
    }