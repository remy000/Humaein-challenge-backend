from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Resubmission
from app.schemas import ResubmissionSchema
from app.ai.ai_utils import extract_resubmission_info

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET endpoint to fetch all claims pending resubmission approval
@router.get("/resubmission/pending")
def get_pending_resubmissions(db: Session = Depends(get_db)):
    from app.models import Denial
    resubmissions = db.query(Resubmission).filter(Resubmission.status == "Pending").all()
    results = []
    for r in resubmissions:
        denial = db.query(Denial).filter(Denial.claim_id == r.claim_id).first()
        results.append({
            "claim_id": r.claim_id,
            "denial_reason": denial.reason if denial else None,
            "status": r.status
        })
    return results

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/resubmission")
def resubmit_claim(request: ResubmissionSchema, db: Session = Depends(get_db)):
    import datetime
    from app.models import Denial
    denial = db.query(Denial).filter_by(claim_id=str(request.claim_id)).first()
    if not denial:
        return {"error": "No denial record found for this claim. Cannot process resubmission."}
    if denial.status.lower() != "pending":
        return {"error": f"Claim denial status is '{denial.status}'. Only claims with pending denial can be resubmitted."}
    ai_result = extract_resubmission_info(request.claim_id)
    status = "Resubmitted" if "Resubmitted" in ai_result else "Pending"
    timestamp = datetime.datetime.utcnow().isoformat()
    resubmission = Resubmission(
        claim_id=str(request.claim_id),
        status=status,
        ai_result=str(ai_result),
        timestamp=str(timestamp)
    )
    db.add(resubmission)
    # Update denial status to 'Resubmitted'
    denial.status = "Resubmitted"
    db.add(denial)
    db.commit()
    db.refresh(resubmission)
    return {
        "id": resubmission.id,
        "claim_id": resubmission.claim_id,
        "status": resubmission.status,
        "ai_result": resubmission.ai_result,
        "timestamp": resubmission.timestamp
    }
