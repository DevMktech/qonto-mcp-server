import uuid
import requests
from typing import Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def verify_sepa_payee(iban: str, beneficiary_name: str) -> Dict:
    """
    Run SEPA Verification of Payee (VoP) for a given IBAN/name pair.

    OAuth scope required: payment.write
    Endpoint: POST /v2/sepa/verify_payee

    Returns a payload containing a "proof_token" valid for 23 hours, required
    when initiating a SEPA transfer (see create_sepa_transfer). The token is
    returned regardless of the match result.

    Args:
        iban: Beneficiary IBAN.
        beneficiary_name: Beneficiary name as registered with the bank.
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/sepa/verify_payee"
    payload = {"iban": iban, "beneficiary_name": beneficiary_name}
    try:
        response = requests.post(url, headers=qonto_mcp.headers, json=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to verify SEPA payee: {str(e)}")


@mcp.tool()
def create_sepa_transfer(
    bank_account_id: str,
    amount: str,
    reference: str,
    vop_proof_token: str,
    beneficiary_id: Optional[str] = None,
    beneficiary: Optional[Dict] = None,
    scheduled_date: Optional[str] = None,
    note: Optional[str] = None,
    attachment_ids: Optional[List[str]] = None,
    idempotency_key: Optional[str] = None,
) -> Dict:
    """
    Create a SEPA transfer.

    OAuth scope required: payment.write
    Endpoint: POST /v2/sepa/transfers

    ⚠️ This is a financial action that moves real money. Strong Customer
    Authentication is required unless the beneficiary is trusted (trusting via
    API is reserved to Embed partners). For one-off untrusted beneficiaries,
    the call will require an SCA flow that this tool does not perform.

    Args:
        bank_account_id: UUID of the debit bank account.
        amount: Decimal amount as string (e.g. "100.50").
        reference: Transfer reference (max 140 chars).
        vop_proof_token: Proof token from verify_sepa_payee, valid 23 hours.
        beneficiary_id: UUID of an existing beneficiary. Provide this OR
            "beneficiary".
        beneficiary: Inline untrusted beneficiary dict
            {"name": "...", "iban": "...", "bic": "...", "email": "...",
             "activity_tag": "..."}.
        scheduled_date: Optional YYYY-MM-DD execution date.
        note: Optional internal note.
        attachment_ids: Optional list of attachment UUIDs (max 5; required for
            transfers over EUR 30,000).
        idempotency_key: UUID used as the X-Qonto-Idempotency-Key header. A
            random UUID is generated if not provided.
    """
    if (beneficiary_id is None) == (beneficiary is None):
        raise ValueError("Provide exactly one of beneficiary_id or beneficiary.")

    url = f"{qonto_mcp.thirdparty_host}/v2/sepa/transfers"
    transfer: Dict = {
        "bank_account_id": bank_account_id,
        "amount": amount,
        "reference": reference,
    }
    if beneficiary_id is not None:
        transfer["beneficiary_id"] = beneficiary_id
    if beneficiary is not None:
        transfer["beneficiary"] = beneficiary
    if scheduled_date is not None:
        transfer["scheduled_date"] = scheduled_date
    if note is not None:
        transfer["note"] = note
    if attachment_ids is not None:
        transfer["attachment_ids"] = attachment_ids

    headers = dict(qonto_mcp.headers)
    headers["X-Qonto-Idempotency-Key"] = idempotency_key or str(uuid.uuid4())

    payload = {"vop_proof_token": vop_proof_token, "transfer": transfer}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create SEPA transfer: {str(e)}")
