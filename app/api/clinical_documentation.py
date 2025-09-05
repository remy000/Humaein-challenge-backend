from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import ClinicalDocumentation
from app.schemas import ClinicalDocumentationSchema
import datetime


router = APIRouter()

# Fetch prior-authorized patients for clinical documentation dropdown
from app.models import PriorAuth
@router.get("/clinical-documentation/authorized")
def get_authorized_docs(db: Session = Depends(get_db)):
    # Get all prior-authorized patient/procedure pairs
    prior_auths = db.query(PriorAuth).filter(PriorAuth.status.in_(["Approved", "PriorAuthApproved"])).all()
    # Return all prior-auth users for dropdown, regardless of clinical documentation
    return [
        {
            "id": pa.id,
            "patient_name": pa.patient_name,
            "insurance_id": pa.insurance_id,
            "procedure": pa.procedure,
            "timestamp": pa.timestamp if hasattr(pa, "timestamp") else None
        }
        for pa in prior_auths
    ]

@router.post("/clinical-documentation")
def submit_clinical_documentation(data: dict, db: Session = Depends(get_db)):
    patient_name = data.get('patient_name', '')
    insurance_id = data.get('insurance_id', '')
    procedure = data.get('procedure', '')
    note = data.get('note', '')
    timestamp = datetime.datetime.utcnow().isoformat()
    if not patient_name or not insurance_id or not procedure or not note:
        raise HTTPException(status_code=400, detail="All fields are required.")
    doc = ClinicalDocumentation(
        patient_name=patient_name,
        insurance_id=insurance_id,
        procedure=procedure,
        note=note,
        timestamp=timestamp
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "id": doc.id,
        "patient_name": doc.patient_name,
        "insurance_id": doc.insurance_id,
        "procedure": doc.procedure,
        "note": doc.note,
        "timestamp": doc.timestamp
    }

@router.get("/clinical-documentation/all")
def get_all_clinical_documentation(db: Session = Depends(get_db)):
    docs = db.query(ClinicalDocumentation).all()
    return [
        {
            "id": d.id,
            "patient_name": d.patient_name,
            "insurance_id": d.insurance_id,
            "procedure": d.procedure,
            "note": d.note,
            "timestamp": d.timestamp
        }
        for d in docs
    ]
