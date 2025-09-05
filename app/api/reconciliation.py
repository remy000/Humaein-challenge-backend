from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Reconciliation
from app.schemas import ReconciliationSchema
from app.ai.ai_utils import extract_reconciliation_info

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/reconciliation")
def reconcile(request: ReconciliationSchema, db: Session = Depends(get_db)):
    import datetime
    from app.models import Claim, Remittance, Denial, Resubmission
    # Validate claim exists
    claim = db.query(Claim).filter_by(claim_id=request.claim_id).first()
    if not claim:
        return {"error": "Claim not found. Cannot reconcile."}
    # Validate remittance is complete
    remittance = db.query(Remittance).filter_by(claim_id=request.claim_id, status="Tracked").first()
    if not remittance:
        return {"error": "Remittance not complete for this claim. Cannot reconcile."}
    # Validate denial/resubmission is resolved (if any)
    denial = db.query(Denial).filter_by(claim_id=request.claim_id).first()
    resubmission = db.query(Resubmission).filter_by(claim_id=request.claim_id).first()
    if denial and denial.status.lower() == "pending":
        return {"error": "Denial is still pending for this claim. Cannot reconcile."}
    if resubmission and resubmission.status.lower() == "pending":
        return {"error": "Resubmission is still pending for this claim. Cannot reconcile."}
    ai_result = extract_reconciliation_info(request.claim_id)
    status = "Reconciled" if "Reconciled" in ai_result else "Pending"
    timestamp = datetime.datetime.utcnow().isoformat()
    notes = ai_result
    reconciliation = Reconciliation(
        claim_id=request.claim_id,
        status=status,
        ai_result=ai_result,
        notes=notes,
        timestamp=timestamp
    )
    db.add(reconciliation)
    db.commit()
    db.refresh(reconciliation)
    return {
        "id": reconciliation.id,
        "claim_id": reconciliation.claim_id,
        "status": reconciliation.status,
        "ai_result": reconciliation.ai_result,
        "notes": reconciliation.notes,
        "timestamp": reconciliation.timestamp
    }
