import requests
from typing import Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def create_quote(
    client_id: str,
    issue_date: str,
    expiry_date: str,
    terms_and_conditions: str,
    items: List[Dict],
    number: Optional[str] = None,
    currency: Optional[str] = "EUR",
    header: Optional[str] = None,
    footer: Optional[str] = None,
    discount: Optional[Dict] = None,
    settings: Optional[Dict] = None,
    upload_id: Optional[str] = None,
    welfare_fund: Optional[Dict] = None,
    withholding_tax: Optional[Dict] = None,
    stamp_duty_amount: Optional[str] = None,
) -> Dict:
    """
    Create a quote (devis) on Qonto.

    OAuth scope required: client_invoice.write
    Endpoint: POST /v2/quotes

    Args:
        client_id: UUID of the client.
        issue_date: ISO date (YYYY-MM-DD).
        expiry_date: ISO date (YYYY-MM-DD).
        terms_and_conditions: Terms and conditions text (max 3000 chars).
        items: List of line items. Each item requires title, currency, quantity,
            unit_price ({"value": "...", "currency": "..."}) and vat_rate. Optional
            per-item fields: description, unit, discount, vat_exemption_reason.
        number: Quote number (required only if automatic numbering is disabled).
        currency: ISO 4217 alpha-3 currency code (default "EUR").
        header, footer: Optional text fields (max 1000 chars each).
        discount: Optional global discount {"type": "...", "value": "..."}.
        settings: Optional organization property overrides for this quote.
        upload_id: Optional UUID of a previously uploaded file attachment.
        welfare_fund, withholding_tax, stamp_duty_amount: Italian-specific options.
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/quotes"
    payload: Dict = {
        "client_id": client_id,
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "terms_and_conditions": terms_and_conditions,
        "currency": currency,
        "items": items,
    }
    optional_fields = {
        "number": number,
        "header": header,
        "footer": footer,
        "discount": discount,
        "settings": settings,
        "upload_id": upload_id,
        "welfare_fund": welfare_fund,
        "withholding_tax": withholding_tax,
        "stamp_duty_amount": stamp_duty_amount,
    }
    for key, value in optional_fields.items():
        if value is not None:
            payload[key] = value

    try:
        response = requests.post(url, headers=qonto_mcp.headers, json=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create quote: {str(e)}")
