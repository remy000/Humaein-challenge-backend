from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import EligibilityRequest, PriorAuth, CodingRequest, ClinicalDocumentation
from app.ai.ai_utils import extract_coding_info

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/coding/by-clinical-doc/{clinical_doc_id}")
def get_coding_by_clinical_doc(clinical_doc_id: int, db: Session = Depends(get_db)):
    clinical_doc = db.query(ClinicalDocumentation).filter_by(id=clinical_doc_id).first()
    if not clinical_doc:
        raise HTTPException(status_code=404, detail="Clinical documentation not found.")
    coding = db.query(CodingRequest).filter_by(documentation=clinical_doc.note).first()
    if not coding:
        return {"icd10_codes": "", "cpt_codes": ""}
    return {
        "icd10_codes": coding.icd10_codes,
        "cpt_codes": coding.cpt_codes,
        "coding_id": coding.id
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import EligibilityRequest, PriorAuth, CodingRequest, ClinicalDocumentation
from app.ai.ai_utils import extract_coding_info

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/coding")
def medical_coding(data: dict, db: Session = Depends(get_db)):
    clinical_doc_id = data.get('clinical_documentation_id')
    if not clinical_doc_id:
        raise HTTPException(status_code=400, detail="clinical_documentation_id is required.")
    clinical_doc = db.query(ClinicalDocumentation).filter_by(id=clinical_doc_id).first()
    if not clinical_doc:
        raise HTTPException(status_code=404, detail="Clinical documentation not found.")
    patient_name = clinical_doc.patient_name
    insurance_id = clinical_doc.insurance_id
    procedure = clinical_doc.procedure
    documentation = clinical_doc.note
    # Check eligibility (accept both 'Eligible' and 'PriorAuthApproved', case-insensitive)
    eligibility = db.query(EligibilityRequest).filter(
        EligibilityRequest.patient_name == patient_name,
        EligibilityRequest.insurance_id == insurance_id,
        EligibilityRequest.status.in_(["Eligible", "PriorAuthApproved", "Approved"])
    ).first()
    if not eligibility:
        raise HTTPException(status_code=400, detail="Eligibility not found or not approved for this patient/insurance.")
    # Check prior-auth (case-insensitive)
    prior_auth = db.query(PriorAuth).filter(
        PriorAuth.patient_name == patient_name,
        PriorAuth.insurance_id == insurance_id,
        PriorAuth.status.in_(["Approved", "approved"])
    ).first()
    if not prior_auth:
        raise HTTPException(status_code=400, detail="Prior authorization not found or not approved for this patient/insurance.")

    # AI coding
    codes = extract_coding_info(documentation)
    # Save coding result to DB
    coding_entry = CodingRequest(
        patient_name=patient_name,
        insurance_id=insurance_id,
        procedure=procedure,
        documentation=documentation,
        icd10_codes=codes.split('\n')[0].replace('ICD-10 Code: ', ''),
        cpt_codes=codes.split('\n')[1].replace('CPT Code: ', '') if '\n' in codes else '',
        status="Completed",
        ai_result=codes
    )
    db.add(coding_entry)
    db.commit()
    db.refresh(coding_entry)
    return {
        "codes": codes,
        "patient_name": patient_name,
        "insurance_id": insurance_id,
        "procedure": procedure,
        "documentation": documentation,
        "coding_id": coding_entry.id
    }
