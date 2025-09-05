# --- Reconciliation Table ---

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class PriorAuth(Base):
    __tablename__ = "prior_auths"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    insurance_id = Column(String, index=True)
    procedure = Column(String)  # <-- Add this line
    status = Column(String, default="Pending")
    ai_result = Column(String)

class Reconciliation(Base):
    __tablename__ = "reconciliations"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    status = Column(String, default="Reconciled")
    ai_result = Column(String)
    notes = Column(String)
    timestamp = Column(String)

class EligibilityRequest(Base):
    __tablename__ = "eligibility_requests"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    insurance_id = Column(String, index=True)
    status = Column(String, default="Pending")

class Remittance(Base):
    __tablename__ = "remittances"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    amount = Column(String)
    status = Column(String, default="Tracked")
    ai_result = Column(String)
    payer_response = Column(String)
    notes = Column(String)

class Denial(Base):
    __tablename__ = "denials"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    reason = Column(String)
    status = Column(String, default="Managed")
    ai_result = Column(String)

class Resubmission(Base):
    __tablename__ = "resubmissions"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    status = Column(String, default="Resubmitted")
    ai_result = Column(String)
    timestamp = Column(String)  # ISO format string for audit

# --- Claims Table ---
class Claim(Base):
    __tablename__ = "claims"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    patient_name = Column(String, index=True)
    insurance_id = Column(String, index=True)
    procedure = Column(String)
    icd10_codes = Column(String)
    cpt_codes = Column(String)
    amount = Column(String)
    details = Column(String)
    status = Column(String, default="Submitted")
    ai_result = Column(String)

class CodingRequest(Base):
    __tablename__ = "coding_requests"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    insurance_id = Column(String, index=True)
    procedure = Column(String)
    documentation = Column(String)
    icd10_codes = Column(String)
    cpt_codes = Column(String)
    status = Column(String, default="Completed")
    ai_result = Column(String)

class ClinicalDocumentation(Base):
    __tablename__ = "clinical_documentation"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    insurance_id = Column(String, index=True)
    procedure = Column(String)
    note = Column(String)
    timestamp = Column(String)

# --- Claim Scrubbing Table ---
class ClaimScrubbing(Base):
    __tablename__ = "claim_scrubbing"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    patient_name = Column(String, index=True)
    insurance_id = Column(String, index=True)
    procedure = Column(String)
    icd10_codes = Column(String)
    cpt_codes = Column(String)
    amount = Column(String)
    status = Column(String, default="Pending")
    errors = Column(String)  # comma-separated errors found
    corrections = Column(String)  # comma-separated corrections made
    ai_result = Column(String)
    timestamp = Column(String)
