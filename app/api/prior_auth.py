from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import EligibilityRequest, PriorAuth
from app.schemas import PriorAuthSchema
from app.ai.ai_utils import extract_prior_auth_info


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fetch prior-authorized patients for clinical documentation dropdown
@router.get("/prior-auth/authorized")
def get_authorized_patients(db: Session = Depends(get_db)):
    records = db.query(PriorAuth).filter(PriorAuth.status.in_(["Approved", "PriorAuthApproved"])).all()
    return [
        {
            "patient_name": r.patient_name,
            "insurance_id": r.insurance_id,
            "procedure": r.procedure
        }
        for r in records
    ]

# List all eligibility records for debugging
@router.get("/eligibility-records")
def list_eligibility_records(db: Session = Depends(get_db)):
    from app.schemas import EligibilityRequestSchema
    records = db.query(EligibilityRequest).all()
    return [EligibilityRequestSchema.from_orm(r) for r in records]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import EligibilityRequest, PriorAuth
from app.schemas import PriorAuthSchema
from app.ai.ai_utils import extract_prior_auth_info

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/prior-auth")
def prior_auth(data: dict, db: Session = Depends(get_db)):
    # Validate eligibility before prior-auth
    patient_name = data.get("patient_name")
    insurance_id = data.get("insurance_id")
    procedure = data.get("procedure", "")
    eligibility = db.query(EligibilityRequest).filter_by(patient_name=patient_name, insurance_id=insurance_id, status="Eligible").first()
    if not eligibility:
        raise HTTPException(status_code=400, detail="Eligibility not found or not approved for this patient/insurance.")
    # AI logic for prior auth
    ai_result = extract_prior_auth_info(patient_name, insurance_id, procedure)
    prior_auth = PriorAuth(
        patient_name=patient_name,
        insurance_id=insurance_id,
        procedure=procedure,
        status="Approved" if "Approved" in ai_result else "Pending",
        ai_result=ai_result
    )
    db.add(prior_auth)
    # Optionally, update eligibility record to reflect prior-auth step
    eligibility.status = "PriorAuthApproved"
    db.commit()
    db.refresh(prior_auth)
    db.refresh(eligibility)
    return PriorAuthSchema.from_orm(prior_auth)
