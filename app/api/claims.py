
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import ClaimRequest, ClaimResponse
from app.models import EligibilityRequest, PriorAuth, CodingRequest
from sqlalchemy.orm import Session
from app.db import get_db
from app.ai.ai_utils import extract_claim_info
import uuid


router = APIRouter()

@router.get("/claims/all")
def get_all_claims(db: Session = Depends(get_db)):
    from app.models import Claim
    claims = db.query(Claim).all()
    return [
        {
            "claim_id": c.claim_id,
            "patient_name": c.patient_name,
            "insurance_id": c.insurance_id,
            "procedure": c.procedure,
            "icd10_codes": c.icd10_codes,
            "cpt_codes": c.cpt_codes,
            "amount": c.amount,
            "details": c.details,
            "status": c.status,
            "ai_result": c.ai_result
        }
        for c in claims
    ]

@router.post("/claims", response_model=ClaimResponse)
def submit_claim(request: ClaimRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Incoming claim request: patient_name={request.patient_name}, insurance_id={request.insurance_id}, procedure={request.procedure}")
    # Validate dependencies
    eligibility = db.query(EligibilityRequest).filter_by(patient_name=request.patient_name, insurance_id=request.insurance_id).first()
    valid_statuses = ["eligible", "priorauthapproved", "approved", "completed"]
    status_ok = eligibility and eligibility.status and eligibility.status.strip().lower() in valid_statuses
    if not status_ok:
        # Try to find eligibility with status PriorAuthApproved (case-insensitive)
        eligibility = db.query(EligibilityRequest).filter_by(patient_name=request.patient_name, insurance_id=request.insurance_id).filter(EligibilityRequest.status.ilike("%priorauthapproved%"))
        eligibility = eligibility.first()
        status_ok = eligibility and eligibility.status and eligibility.status.strip().lower() in valid_statuses
    if not status_ok:
        print(f"Claim error: Patient not eligible. Found: {eligibility.status if eligibility else 'None'} for {request.patient_name}, {request.insurance_id}")
        raise HTTPException(status_code=400, detail="Patient not eligible.")
    prior_auth = db.query(PriorAuth).filter_by(patient_name=request.patient_name, procedure=request.procedure).first()
    if not prior_auth or prior_auth.status.lower() not in ["approved", "priorauthapproved"]:
        print(f"Claim error: Procedure not prior authorized. Found: {prior_auth.status if prior_auth else 'None'} for {request.patient_name}, {request.procedure}")
        raise HTTPException(status_code=400, detail="Procedure not prior authorized.")
    coding = db.query(CodingRequest).filter_by(patient_name=request.patient_name, procedure=request.procedure).first()
    if not coding or not coding.icd10_codes or not coding.cpt_codes:
        print(f"Claim error: Missing valid ICD-10/CPT codes. Found: {coding.icd10_codes if coding else 'None'}, {coding.cpt_codes if coding else 'None'} for {request.patient_name}, {request.procedure}")
        raise HTTPException(status_code=400, detail="Missing valid ICD-10/CPT codes.")
    # Generate claim ID
    claim_id = str(uuid.uuid4())
    # Mock AI logic for claim status and details
    ai_result = extract_claim_info(
        patient_name=request.patient_name,
        insurance_id=request.insurance_id,
        procedure=request.procedure,
        icd10_codes=request.icd10_codes,
        cpt_codes=request.cpt_codes,
        amount=request.amount,
        details=request.details
    )
    # Save claim to DB
    from app.models import Claim
    claim_entry = Claim(
        claim_id=claim_id,
        patient_name=request.patient_name,
        insurance_id=request.insurance_id,
        procedure=request.procedure,
        icd10_codes=request.icd10_codes,
        cpt_codes=request.cpt_codes,
        amount=request.amount,
        details=request.details,
        status=ai_result["status"],
        ai_result=str(ai_result)
    )
    db.add(claim_entry)
    db.commit()
    db.refresh(claim_entry)
    return ClaimResponse(
        claim_id=claim_id,
        status=ai_result["status"],
        details=ai_result["details"]
    )
