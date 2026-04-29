import requests
from typing import Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def get_clients(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
) -> Dict:
    """
    Get all clients from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.

    Example: get_clients(per_page=20)
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/clients"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Error fetching clients: {str(e)}")


@mcp.tool()
def get_client(client_id: str) -> Dict:
    """
    Get a specific client from Qonto API.

    Args:
        client_id: The ID of the client to retrieve.

    Example: get_client(client_id="a1b2c3d4-5678-90ab-cdef-ghijklmnopqr")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/clients/{client_id}"

    try:
        response = requests.get(url, headers=qonto_mcp.headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Error getting client: {str(e)}")


@mcp.tool()
def create_client(
    kind: str,
    name: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    extra_emails: Optional[List[str]] = None,
    phone: Optional[Dict] = None,
    vat_number: Optional[str] = None,
    tax_identification_number: Optional[str] = None,
    currency: Optional[str] = None,
    locale: Optional[str] = None,
    billing_address: Optional[Dict] = None,
    delivery_address: Optional[Dict] = None,
    e_invoicing_address: Optional[str] = None,
    recipient_code: Optional[str] = None,
) -> Dict:
    """
    Create a client on Qonto.

    OAuth scope required: client.write
    Endpoint: POST /v2/clients

    Args:
        kind: "individual", "freelancer" or "company".
        name: Required for company clients (max 250 chars).
        first_name, last_name: Required for individual/freelancer (max 60 chars each).
        email: Optional email.
        extra_emails: Optional list of additional emails (max 100).
        phone: Optional dict {"country_code": "...", "number": "..."}.
        vat_number, tax_identification_number: Optional (max 20 chars each).
        currency: ISO 4217 (required if the client will be used for invoicing).
        locale: "fr" / "en" / "it" / "de" / "es" (required for invoicing).
        billing_address: Dict with street_address, city, zip_code, province_code,
            country_code. Required for invoicing.
        delivery_address: Same structure as billing_address.
        e_invoicing_address: French-specific.
        recipient_code: Italian-only.
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/clients"
    payload: Dict = {"kind": kind}
    optional_fields = {
        "name": name,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "extra_emails": extra_emails,
        "phone": phone,
        "vat_number": vat_number,
        "tax_identification_number": tax_identification_number,
        "currency": currency,
        "locale": locale,
        "billing_address": billing_address,
        "delivery_address": delivery_address,
        "e_invoicing_address": e_invoicing_address,
        "recipient_code": recipient_code,
    }
    for key, value in optional_fields.items():
        if value is not None:
            payload[key] = value

    try:
        response = requests.post(url, headers=qonto_mcp.headers, json=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create client: {str(e)}")
