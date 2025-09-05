from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import EligibilityRequest
from app.schemas import EligibilityRequestSchema
from app.ai.ai_utils import extract_eligibility_info


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fetch all eligible patients for prior-auth dropdown
@router.get("/eligibility/eligible")
def get_eligible_patients(db: Session = Depends(get_db)):
    records = db.query(EligibilityRequest).filter(EligibilityRequest.status.in_(["Eligible", "PriorAuthApproved", "Approved"])).all()
    return [
        {
            "patient_name": r.patient_name,
            "insurance_id": r.insurance_id
        }
        for r in records
    ]

@router.post("/eligibility")
def check_eligibility(request: EligibilityRequestSchema, db: Session = Depends(get_db)):
    ai_result = extract_eligibility_info(request.patient_name, request.insurance_id)
    status = ai_result["status"]
    eligibility = EligibilityRequest(
        patient_name=request.patient_name,
        insurance_id=request.insurance_id,
        status=status
    )
    db.add(eligibility)
    db.commit()
    db.refresh(eligibility)
    return {
        "id": eligibility.id,
        "status": eligibility.status,
        "ai_response": ai_result["ai_response"]
    }
