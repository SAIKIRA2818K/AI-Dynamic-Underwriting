from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.underwriting import UnderwritingRequest, UnderwritingResponse
from app.db.session import get_db
from app.services.underwriting import UnderwritingService

router = APIRouter()

@router.post("/evaluate", response_model=UnderwritingResponse, status_code=status.HTTP_200_OK)
def evaluate_loan_application(
    request: UnderwritingRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluates loan application risk using XGBoost and Isolation Forest models.
    Generates natural language explanations using the OpenAI API.
    """
    try:
        service = UnderwritingService(db=db)
        evaluation = service.evaluate(request)
        return evaluation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )
