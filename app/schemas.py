from pydantic import BaseModel

class PriorAuthSchema(BaseModel):
    patient_name: str
    insurance_id: str
    status: str = "Pending"
    ai_result: str = ""

    class Config:
        from_attributes = True


class EligibilityRequestSchema(BaseModel):
    patient_name: str
    insurance_id: str
    status: str = "Pending"

    class Config:
        from_attributes = True

class RemittanceSchema(BaseModel):
    claim_id: str
    amount: str
    status: str = "Tracked"
    ai_result: str = ""
    payer_response: str = ""
    notes: str = ""

    class Config:
        from_attributes = True

class DenialSchema(BaseModel):
    claim_id: str
    reason: str
    status: str = "Pending"
    ai_result: str = ""

    class Config:
        from_attributes = True

class ResubmissionSchema(BaseModel):
    claim_id: str
    status: str = "Resubmitted"
    ai_result: str = ""
    timestamp: str = ""

    class Config:
        from_attributes = True


    class Config:
        from_attributes = True

class ReconciliationSchema(BaseModel):
    claim_id: str
    status: str = "Reconciled"

    class Config:
        from_attributes = True

class ClaimRequest(BaseModel):
    patient_name: str
    insurance_id: str
    procedure: str
    icd10_codes: str
    cpt_codes: str
    amount: str = ""
    details: str = ""

class ClaimResponse(BaseModel):
    claim_id: str
    status: str
    details: dict

class ClinicalDocumentationSchema(BaseModel):
    patient_name: str
    insurance_id: str
    procedure: str
    note: str
    timestamp: str = ""

    class Config:
        from_attributes = True

# --- Claim Scrubbing Schemas ---
class ClaimScrubbingSchema(BaseModel):
    claim_id: str
    patient_name: str
    insurance_id: str
    procedure: str
    icd10_codes: str
    cpt_codes: str
    amount: str = ""
    status: str = "Pending"
    errors: str = ""
    corrections: str = ""
    ai_result: str = ""
    timestamp: str = ""

    class Config:
        from_attributes = True
