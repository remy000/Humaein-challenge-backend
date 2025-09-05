from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import ClaimScrubbing, Claim
from app.schemas import ClaimScrubbingSchema
from datetime import datetime

router = APIRouter()

@router.post("/claim-scrubbing", response_model=ClaimScrubbingSchema)
def scrub_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        return {"error": "Claim not found"}
    # Demo AI logic: check for missing codes, invalid amount, etc.
    errors = []
    corrections = []
    if not claim.icd10_codes:
        errors.append("Missing ICD-10 codes")
        corrections.append("Request ICD-10 codes from coder")
    if not claim.cpt_codes:
        errors.append("Missing CPT codes")
        corrections.append("Request CPT codes from coder")
    if not claim.amount or claim.amount == "0":
        errors.append("Missing or zero claim amount")
        corrections.append("Verify claim amount")
    # Add more rules as needed
    status = "Clean" if not errors else "Needs Correction"
    ai_result = f"Errors: {', '.join(errors)}; Corrections: {', '.join(corrections)}"
    scrubbing = ClaimScrubbing(
        claim_id=claim.claim_id,
        patient_name=claim.patient_name,
        insurance_id=claim.insurance_id,
        procedure=claim.procedure,
        icd10_codes=claim.icd10_codes,
        cpt_codes=claim.cpt_codes,
        amount=claim.amount,
        status=status,
        errors=", ".join(errors),
        corrections=", ".join(corrections),
        ai_result=ai_result,
        timestamp=datetime.utcnow().isoformat()
    )
    db.add(scrubbing)
    db.commit()
    db.refresh(scrubbing)
    return scrubbing

@router.get("/claim-scrubbing/{claim_id}", response_model=ClaimScrubbingSchema)
def get_scrubbing_result(claim_id: str, db: Session = Depends(get_db)):
    scrubbing = db.query(ClaimScrubbing).filter(ClaimScrubbing.claim_id == claim_id).first()
    if not scrubbing:
        return {"error": "Scrubbing result not found"}
    return scrubbing
