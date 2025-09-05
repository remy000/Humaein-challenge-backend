from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db import get_db
from sqlalchemy import func
from app.models import EligibilityRequest, Denial, Remittance, Reconciliation, Resubmission

router = APIRouter()

@router.get("/dashboard-stats")
def dashboard_stats(db: Session = Depends(get_db)):
    eligibility_count = db.query(EligibilityRequest).count()
    denial_count = db.query(Denial).filter(Denial.status == "Pending").count()
    remittance_count = db.query(Remittance).count()
    reconciliation_count = db.query(Reconciliation).count()
    resubmission_count = db.query(Resubmission).filter_by(status="Resubmitted").count()
    return {
        "eligibility": eligibility_count,
        "denial": denial_count,
        "remittance": remittance_count,
        "reconciliation": reconciliation_count,
        "resubmission": resubmission_count
    }
