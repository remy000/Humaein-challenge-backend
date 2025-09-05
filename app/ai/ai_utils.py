# OpenAI integration for AI requests
import os
import requests

# OpenAI integration for AI requests

# def ai_request(prompt: str, max_tokens: int = 100) -> str:
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     if not OPENAI_API_KEY:
#         return "AI error: OPENAI_API_KEY environment variable not set"
#     openai.api_key = OPENAI_API_KEY
#     try:
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant for RCM automation."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=max_tokens,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"AI error: {str(e)}"



# ...existing code...
# from transformers import pipeline
# # Load the smallest available LLaMA model (Llama-2-7b-hf)
# llama_model = pipeline("text-generation", model="meta-llama/Llama-2-7b-hf")

# def ai_request(prompt: str, max_tokens: int = 100) -> str:
#     result = llama_model(prompt, max_new_tokens=max_tokens, do_sample=True)
#     return result[0]['generated_text'].strip()


# --- Small Model for Local CPU Inference ---

# HF_API_URL = "https://api-inference.huggingface.co/models/nlpaueb/clinical-icd10-coding"
# HF_API_KEY = os.getenv("HF_API_KEY")  # set this in your environment variables
# headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

# def ai_request(prompt: str) -> str:
#     """
#     Sends prompt to Hugging Face clinical coding model.
#     Falls back to simple echo if API key not set.
#     """
#     if not HF_API_KEY:
#         return f"[Mock AI Response] (No Hugging Face API key set): {prompt}"

#     try:
#         response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
#         if response.status_code != 200:
#             return f"AI error: {response.status_code} - {response.text}"
#         result = response.json()
#         # Hugging Face returns a list of dicts; extract text safely
#         if isinstance(result, list) and len(result) > 0:
#             return result[0].get("generated_text", str(result))
#         return str(result)
#     except Exception as e:
#         return f"AI error: {str(e)}"

# Load distilgpt2 model (small, fast, open-access, good for CPU)

# Hugging Face Inference API for flan-t5-base
HF_API_KEY = os.getenv("HF_API_KEY")  # Set this in Railway or your .env
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

def ai_request(prompt: str) -> str:
    if not HF_API_KEY:
        return f"[Mock AI Response] (No Hugging Face API key set): {prompt}"
    try:
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code != 200:
            return f"AI error: {response.status_code} - {response.text}"
        result = response.json()
        # Hugging Face returns a list of dicts; extract text safely
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", str(result))
        return str(result)
    except Exception as e:
        return f"AI error: {str(e)}"


def extract_eligibility_info(patient_name: str, insurance_id: str) -> dict:
    prompt = f"Check insurance eligibility for patient '{patient_name}' with insurance ID '{insurance_id}'. Return status and reason."
    ai_result = ai_request(prompt)
    # Fallback logic: if the model just echoes the prompt or gives a generic answer, return mock result
    if (prompt in ai_result) or ("subject to change" in ai_result.lower()) or (len(ai_result.strip()) < 40):
        return {
            "status": "Eligible",
            "ai_response": f"Eligibility status for {patient_name} (ID: {insurance_id}): Approved. Reason: Active coverage, no outstanding issues."
        }
    # Try to parse status from AI result
    status = "Eligible" if "eligible" in ai_result.lower() else "Not Eligible" if "not eligible" in ai_result.lower() else "Unknown"
    return {
        "status": status,
        "ai_response": ai_result.strip()
    }

def extract_remittance_info(claim_id: str, amount: str) -> str:
    prompt = f"Track remittance for claim ID '{claim_id}' with amount '{amount}'. Return remittance status and notes."
    ai_result = ai_request(prompt)
    if (prompt in ai_result) or (len(ai_result.strip()) < 40):
        return f"Remittance for claim {claim_id} (amount: {amount}): Paid in full. No outstanding balance."
    return ai_result

def extract_denial_info(claim_id: str, reason: str) -> str:
    prompt = f"Analyze denial for claim ID '{claim_id}'. Reason: '{reason}'. Suggest management actions."
    ai_result = ai_request(prompt)
    if (prompt in ai_result) or (len(ai_result.strip()) < 40):
        return f"Denial for claim {claim_id}: Reason - {reason}. Suggested action: Review documentation and resubmit with additional information."
    return ai_result

def extract_resubmission_info(claim_id: str) -> str:
    prompt = f"A claim with ID '{claim_id}' has been resubmitted. What is the next status update for the user?"
    ai_result = ai_request(prompt)
    # Always return a user-friendly message for resubmission
    if (prompt in ai_result) or (len(ai_result.strip()) < 40):
        return f"Claim {claim_id} has been resubmitted and is now under review. You will be notified once the payer processes your claim."
    return ai_result

def extract_reconciliation_info(claim_id: str) -> str:
    prompt = f"Reconcile claim ID '{claim_id}'. Return reconciliation status and any discrepancies."
    ai_result = ai_request(prompt)
    if (prompt in ai_result) or (len(ai_result.strip()) < 40):
        return f"Reconciliation for claim {claim_id}: Status - Complete. No discrepancies found."
    return ai_result

def extract_prior_auth_info(patient_name: str, insurance_id: str, procedure: str = "") -> str:
    prompt = f"Request prior authorization for patient '{patient_name}' with insurance ID '{insurance_id}' for procedure '{procedure}'. Return approval status and reason."
    ai_result = ai_request(prompt)
    if (prompt in ai_result) or (len(ai_result.strip()) < 40):
        return f"Prior authorization for {patient_name} (ID: {insurance_id}, procedure: {procedure}): Approved. Reason: Meets coverage criteria."
    return ai_result

def extract_coding_info(documentation: str) -> str:
    prompt = f"Given this clinical note, suggest ICD-10 and CPT codes. Return JSON. Note: {documentation}"
    ai_result = ai_request(prompt)
    # Fallback: If output is generic, too short, or just repeats the prompt, return mock codes
    if (prompt in ai_result) or ("ICD" not in ai_result and "CPT" not in ai_result) or len(ai_result.strip()) < 40:
        return "ICD-10 Code: G44.1 (Vascular headache)\nCPT Code: 70551 (MRI, brain, without contrast)"
    return ai_result.strip()

def extract_claim_info(patient_name: str, insurance_id: str, procedure: str, icd10_codes: str, cpt_codes: str, amount: str = "", details: str = "") -> dict:
    # Always return realistic mock claim response for demo
    return {
        "status": "Submitted",
        "details": {
            "patient_name": patient_name,
            "insurance_id": insurance_id,
            "procedure": procedure,
            "icd10_codes": icd10_codes,
            "cpt_codes": cpt_codes,
            "amount": amount if amount else "1000.00",
            "payer_response": "Claim received and under review."
        }
    }


# def extract_eligibility_info(patient_name: str, insurance_id: str) -> str:
#     prompt = f"Check insurance eligibility for patient '{patient_name}' with insurance ID '{insurance_id}'. Return status and reason."
#     ai_result = ai_request(prompt)
#     # Fallback logic: if the model just echoes the prompt or gives a generic answer, return a mock result
#     if (prompt in ai_result) or ("subject to change" in ai_result.lower()) or (len(ai_result.strip()) < 40):
#         return f"Eligibility status for {patient_name} (ID: {insurance_id}): Approved. Reason: Active coverage, no outstanding issues."
#     return ai_result

# def extract_remittance_info(claim_id: str, amount: str) -> str:
#     prompt = f"Track remittance for claim ID '{claim_id}' with amount '{amount}'. Return remittance status and notes."
#     ai_result = ai_request(prompt)
#     if (prompt in ai_result) or (len(ai_result.strip()) < 40):
#         return f"Remittance for claim {claim_id} (amount: {amount}): Paid in full. No outstanding balance."
#     return ai_result

# def extract_denial_info(claim_id: str, reason: str) -> str:
#     prompt = f"Analyze denial for claim ID '{claim_id}'. Reason: '{reason}'. Suggest management actions."
#     ai_result = ai_request(prompt)
#     if (prompt in ai_result) or (len(ai_result.strip()) < 40):
#         return f"Denial for claim {claim_id}: Reason - {reason}. Suggested action: Review documentation and resubmit with additional information."
#     return ai_result

# def extract_resubmission_info(claim_id: str) -> str:
#     prompt = f"Should claim ID '{claim_id}' be resubmitted? Return recommendation and next steps."
#     ai_result = ai_request(prompt)
#     if (prompt in ai_result) or (len(ai_result.strip()) < 40):
#         return f"Claim {claim_id} should be resubmitted. Next steps: Correct any errors, attach supporting documents, and resubmit for review."
#     return ai_result

# def extract_reconciliation_info(claim_id: str) -> str:
#     prompt = f"Reconcile claim ID '{claim_id}'. Return reconciliation status and any discrepancies."
#     ai_result = ai_request(prompt)
#     if (prompt in ai_result) or (len(ai_result.strip()) < 40):
#         return f"Reconciliation for claim {claim_id}: Status - Complete. No discrepancies found."
#     return ai_result

# def extract_prior_auth_info(patient_name: str, insurance_id: str, procedure: str = "") -> str:
#     prompt = f"Request prior authorization for patient '{patient_name}' with insurance ID '{insurance_id}' for procedure '{procedure}'. Return approval status and reason."
#     ai_result = ai_request(prompt)
#     if (prompt in ai_result) or (len(ai_result.strip()) < 40):
#         return f"Prior authorization for {patient_name} (ID: {insurance_id}, procedure: {procedure}): Approved. Reason: Meets coverage criteria."
#     return ai_result
# def extract_coding_info(documentation: str) -> str:
#     prompt = f"Extract ICD-10 and CPT codes from this clinical documentation:\n{documentation}"
#     ai_result = ai_request(prompt)
#     # Fallback: If output is generic, too short, or does not contain codes, return mock codes
#     if ("ICD" not in ai_result and "CPT" not in ai_result) or len(ai_result.strip()) < 40:
#         return "ICD-10 Code: J18.9 (Pneumonia, unspecified organism)\nCPT Code: 99213 (Office visit, established patient)"
#     return ai_result
