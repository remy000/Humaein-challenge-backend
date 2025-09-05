
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api.eligibility import router as eligibility_router
from app.api.prior_auth import router as prior_auth_router
from app.api.coding import router as coding_router
from app.api.claims import router as claims_router
from app.api.remittance import router as remittance_router
from app.api.denial import router as denial_router
from app.api.resubmission import router as resubmission_router
from app.api.resubmission_approve import router as resubmission_approve_router
from app.api.reconciliation import router as reconciliation_router
# Dashboard stats endpoint
from app.api.clinical_documentation import router as clinical_documentation_router
from app.api.claim_scrubbing import router as claim_scrubbing_router
# Dashboard stats endpoint
from app.db import SessionLocal, engine
from app.models import EligibilityRequest, Remittance, Denial, Resubmission, Reconciliation, PriorAuth, Base


app = FastAPI()

# Allow frontend (localhost:3000) to access backend APIs
allowed_origins = os.getenv("ALLOWED_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(eligibility_router)
app.include_router(prior_auth_router)
app.include_router(coding_router)
app.include_router(claims_router)
app.include_router(remittance_router)
app.include_router(denial_router)
app.include_router(resubmission_router)
app.include_router(resubmission_approve_router)


app.include_router(clinical_documentation_router)
app.include_router(reconciliation_router)
app.include_router(claim_scrubbing_router)



# Automatically create all tables if they do not exist
Base.metadata.create_all(bind=engine)
print("[INFO] All tables created (or already exist) in the database.")

@app.get("/dashboard-stats")
def dashboard_stats():
    db = SessionLocal()
    try:
        eligibility_count = db.query(EligibilityRequest).count()
        remittance_count = db.query(Remittance).count()
        denial_count = db.query(Denial).count()
        resubmission_count = db.query(Resubmission).count()
        reconciliation_count = db.query(Reconciliation).count()
        return {
            "eligibility": eligibility_count,
            "remittance": remittance_count,
            "denial": denial_count,
            "resubmission": resubmission_count,
            "reconciliation": reconciliation_count
        }
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-native RCM backend!"}
