from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Remittance, Claim
from app.schemas import RemittanceSchema
from app.ai.ai_utils import extract_remittance_info

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/remittance")
def track_remittance(request: RemittanceSchema, db: Session = Depends(get_db)):
    # Validate claim exists
    claim = db.query(Claim).filter_by(claim_id=request.claim_id).first()
    if not claim:
        return {"error": "Claim not found."}
    ai_result = extract_remittance_info(request.claim_id, request.amount)
    status = "Tracked"
    # Parse AI result for payer_response and notes (simple demo logic)
    payer_response = "Paid in full" if "Paid" in ai_result else "Pending"
    notes = ai_result
    remittance = Remittance(
        claim_id=request.claim_id,
        amount=request.amount,
        status=status,
        ai_result=ai_result,
        payer_response=payer_response,
        notes=notes
    )
    db.add(remittance)
    db.commit()
    db.refresh(remittance)
    return {
        "id": remittance.id,
        "status": remittance.status,
        "ai_result": remittance.ai_result,
        "payer_response": remittance.payer_response,
        "notes": remittance.notes
    }
