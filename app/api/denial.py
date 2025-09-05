from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Denial
from app.schemas import DenialSchema
from app.ai.ai_utils import extract_denial_info

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/denial")
def manage_denial(request: DenialSchema, db: Session = Depends(get_db)):
    # Validate claim existence and status
    from app.models import Claim
    import logging
    logging.basicConfig(level=logging.DEBUG)
    data = request.dict()
    claim_id = data.get("claim_id")
    reason = data.get("reason")
    logging.debug(f"Denial request received: claim_id={claim_id}, reason={reason}")
    claim = db.query(Claim).filter_by(claim_id=claim_id).first()
    if not claim:
        logging.error(f"Claim not found for claim_id={claim_id}")
        return {"error": "Claim not found. Cannot process denial."}
    if not reason:
        logging.error("Denial reason is empty.")
        return {"error": "Denial reason cannot be empty."}
    if claim.status.lower() not in ["submitted", "processed", "denied"]:
        logging.error(f"Claim status '{claim.status}' not eligible for denial.")
        return {"error": f"Claim status '{claim.status}' not eligible for denial."}
    ai_result = extract_denial_info(claim_id, reason)
    status = "Managed" if "Managed" in ai_result else "Pending"
    denial = Denial(
        claim_id=claim_id,
        reason=reason,
        status=status,
        ai_result=ai_result
    )
    db.add(denial)
    db.commit()
    db.refresh(denial)
    logging.debug(f"Denial saved: id={denial.id}, claim_id={denial.claim_id}, reason={denial.reason}, status={denial.status}, ai_result={denial.ai_result}")
    return {"id": denial.id, "claim_id": denial.claim_id, "reason": denial.reason, "status": denial.status, "ai_result": denial.ai_result}
