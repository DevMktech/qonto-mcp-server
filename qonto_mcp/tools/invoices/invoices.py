import requests
from datetime import datetime
from typing import Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def get_client_invoices(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get client invoices from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        status: Filter invoices by status.
        updated_at_from: Filter invoices updated from this date.
        updated_at_to: Filter invoices updated until this date.

    Example: get_client_invoices(per_page=10, status="paid")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/client_invoices"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if status is not None:
        params["status"] = status
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch client invoices {str(e)}")


@mcp.tool()
def get_supplier_invoices(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get supplier invoices from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        status: Filter invoices by status.
        updated_at_from: Filter invoices updated from this date.
        updated_at_to: Filter invoices updated until this date.

    Example: get_supplier_invoices(per_page=10, status="pending")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/supplier_invoices"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if status is not None:
        params["status"] = status
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch supplier invoices {str(e)}")


@mcp.tool()
def get_credit_notes(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get credit notes from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        updated_at_from: Filter credit notes updated from this date.
        updated_at_to: Filter credit notes updated until this date.

    Example: get_credit_notes(per_page=5)
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/credit_notes"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch credit notes {str(e)}")


@mcp.tool()
def create_client_invoice(
    client_id: str,
    issue_date: str,
    due_date: str,
    currency: str,
    payment_methods: Dict,
    items: List[Dict],
    number: Optional[str] = None,
    status: Optional[str] = None,
    upload_id: Optional[str] = None,
    performance_start_date: Optional[str] = None,
    performance_end_date: Optional[str] = None,
    purchase_order: Optional[str] = None,
    terms_and_conditions: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    discount: Optional[Dict] = None,
    settings: Optional[Dict] = None,
    report_einvoicing: Optional[bool] = None,
    payment_reporting: Optional[Dict] = None,
    welfare_fund: Optional[Dict] = None,
    withholding_tax: Optional[Dict] = None,
    stamp_duty_amount: Optional[str] = None,
) -> Dict:
    """
    Create a client invoice on Qonto.

    OAuth scope required: client_invoice.write
    Endpoint: POST /v2/client_invoices

    Args:
        client_id: UUID of the client.
        issue_date: ISO date (YYYY-MM-DD).
        due_date: ISO date (YYYY-MM-DD).
        currency: ISO 4217 alpha-3 (e.g. "EUR").
        payment_methods: Dict containing at least {"iban": "..."}.
        items: Line items. Each requires title, quantity, unit_price ({value, currency})
            and vat_rate. Optional per-item: description, unit, discount,
            vat_exemption_reason.
        number: Invoice number (required only if automatic numbering disabled).
        status: "draft" or "unpaid" (default "unpaid").
        upload_id: Optional UUID of a previously uploaded attachment.
        performance_start_date, performance_end_date: Optional performance period.
        purchase_order: Optional PO reference (max 40 chars).
        terms_and_conditions: Optional (max 525 chars).
        header, footer: Optional text fields.
        discount: Optional global discount {"type": "percentage"|"absolute", "value": "..."}.
        settings: Organization property overrides for this invoice.
        report_einvoicing, payment_reporting, welfare_fund, withholding_tax,
        stamp_duty_amount: Italian/Spanish-specific options.
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/client_invoices"
    payload: Dict = {
        "client_id": client_id,
        "issue_date": issue_date,
        "due_date": due_date,
        "currency": currency,
        "payment_methods": payment_methods,
        "items": items,
    }
    optional_fields = {
        "number": number,
        "status": status,
        "upload_id": upload_id,
        "performance_start_date": performance_start_date,
        "performance_end_date": performance_end_date,
        "purchase_order": purchase_order,
        "terms_and_conditions": terms_and_conditions,
        "header": header,
        "footer": footer,
        "discount": discount,
        "settings": settings,
        "report_einvoicing": report_einvoicing,
        "payment_reporting": payment_reporting,
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
        raise RuntimeError(f"Failed to create client invoice: {str(e)}")


@mcp.tool()
def create_credit_note(
    invoice_id: str,
    issue_date: str,
    currency: str,
    reason: str,
    items: List[Dict],
    number: Optional[str] = None,
    terms_and_conditions: Optional[str] = None,
    contact_email: Optional[str] = None,
    discount: Optional[Dict] = None,
    welfare_fund: Optional[Dict] = None,
    withholding_tax: Optional[Dict] = None,
    stamp_duty_amount: Optional[str] = None,
) -> Dict:
    """
    Create a credit note (avoir) on Qonto.

    OAuth scope required: client_invoices.write
    Endpoint: POST /v2/credit_notes

    Args:
        invoice_id: UUID of the original client invoice.
        issue_date: ISO date (YYYY-MM-DD).
        currency: ISO 4217 alpha-3.
        reason: Reason for the credit note (max 500 chars).
        items: Line items. Each requires title, quantity, unit_price ({value, currency})
            and vat_rate. Optional per-item: description, unit, discount,
            vat_exemption_reason.
        number: Credit note number (required only if automatic numbering disabled).
        terms_and_conditions: Optional (max 525 chars).
        contact_email: Optional contact email.
        discount: Optional global discount {"type": "...", "value": "..."}.
        welfare_fund, withholding_tax, stamp_duty_amount: Italian/Spanish-specific.
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/credit_notes"
    payload: Dict = {
        "invoice_id": invoice_id,
        "issue_date": issue_date,
        "currency": currency,
        "reason": reason,
        "items": items,
    }
    optional_fields = {
        "number": number,
        "terms_and_conditions": terms_and_conditions,
        "contact_email": contact_email,
        "discount": discount,
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
        raise RuntimeError(f"Failed to create credit note: {str(e)}")
