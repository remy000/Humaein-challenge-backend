from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Resubmission

router = APIRouter()

@router.post("/resubmission/approve")
def approve_resubmission(claim_id: str, db: Session = Depends(get_db)):
    resub = db.query(Resubmission).filter_by(claim_id=claim_id).first()
    if not resub:
        return {"error": "Resubmission not found for this claim."}
    resub.status = "Approved"
    db.add(resub)
    db.commit()
    db.refresh(resub)
    return {
        "id": resub.id,
        "claim_id": resub.claim_id,
        "status": resub.status
    }
