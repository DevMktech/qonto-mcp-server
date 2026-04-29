import requests
from typing import Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def list_quotes(
    status: Optional[List[str]] = None,
    created_at_from: Optional[str] = None,
    created_at_to: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    sort_by: Optional[str] = None,
) -> Dict:
    """
    List quotes from Qonto.

    OAuth scope required: client_invoices.read
    Endpoint: GET /v2/quotes

    Args:
        status: Filter by status. Allowed: "pending_approval", "approved", "canceled".
        created_at_from: ISO 8601 datetime lower bound.
        created_at_to: ISO 8601 datetime upper bound.
        page: Page number.
        per_page: Items per page (default 100, max 500).
        sort_by: "created_at:desc" or "created_at:asc".
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/quotes"
    params: Dict = {}
    if status:
        params["filter[status][]"] = status
    if created_at_from is not None:
        params["filter[created_at_from]"] = created_at_from
    if created_at_to is not None:
        params["filter[created_at_to]"] = created_at_to
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if sort_by is not None:
        params["sort_by"] = sort_by

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to list quotes: {str(e)}")


@mcp.tool()
def get_quote(quote_id: str) -> Dict:
    """
    Retrieve a specific quote from Qonto.

    OAuth scope required: client_invoices.read
    Endpoint: GET /v2/quotes/{id}

    Args:
        quote_id: UUID of the quote.
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/quotes/{quote_id}"
    try:
        response = requests.get(url, headers=qonto_mcp.headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to get quote: {str(e)}")


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


@mcp.tool()
def send_quote_by_email(
    quote_id: str,
    send_to: List[str],
    email_title: str,
    email_body: Optional[str] = None,
    copy_to_self: Optional[bool] = None,
) -> Dict:
    """
    Send a quote by email.

    OAuth scope required: client_invoices.write
    Endpoint: POST /v2/quotes/{id}/send

    Args:
        quote_id: UUID of the quote.
        send_to: List of recipient email addresses.
        email_title: Email subject line.
        email_body: Optional message body.
        copy_to_self: Whether to send a copy to the authenticated user (default true).
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/quotes/{quote_id}/send"
    payload: Dict = {"send_to": send_to, "email_title": email_title}
    if email_body is not None:
        payload["email_body"] = email_body
    if copy_to_self is not None:
        payload["copy_to_self"] = copy_to_self

    try:
        response = requests.post(url, headers=qonto_mcp.headers, json=payload)
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return {"status": "sent"}
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to send quote: {str(e)}")
