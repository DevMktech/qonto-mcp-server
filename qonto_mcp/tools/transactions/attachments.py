from typing import Dict, Optional
import os
import mimetypes
import requests
from requests.exceptions import RequestException
import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def list_qonto_transaction_attachments(
    transaction_id: str, page: Optional[str] = None, per_page: Optional[str] = None
):
    """
    Retrieves all attachments for a specific transaction from the Qonto API.

    Attachments represent documents like receipts or invoices linked to transactions.

    Note: The download URLs returned are only valid for 30 minutes. If you need to access
    the files after that time, you'll need to call this function again.

    Args:
        transaction_id: UUID of the transaction to retrieve attachments for
        page: Page number for pagination
        per_page: Number of attachments per page

    Example: list_qonto_transaction_attachments(
                transaction_id='aab86d8a-0d4c-4749-9a49-0ada88a9c423'
             )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/transactions/{transaction_id}/attachments"
    params = {}

    if page:
        params["page"] = page
    if per_page:
        params["per_page"] = per_page

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch transaction attachments {str(e)}")


@mcp.tool()
def upload_transaction_attachment(transaction_id: str, file_path: str) -> Dict:
    """
    Upload an attachment (JPEG, PNG or PDF) to a transaction.

    OAuth scope required: attachment.write
    Endpoint: POST /v2/transactions/{id}/attachments (multipart/form-data)

    Note: the uploaded file is processed in the background, so the attachment
    may not appear immediately on the transaction.

    Args:
        transaction_id: UUID of the transaction.
        file_path: Local filesystem path to the file to attach.
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/transactions/{transaction_id}/attachments"
    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    try:
        with open(file_path, "rb") as fh:
            files = {"file": (filename, fh, mime_type)}
            response = requests.post(url, headers=qonto_mcp.headers, files=files)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {"status": "uploaded"}
            return response.json()
    except (RequestException, OSError) as e:
        raise RuntimeError(f"Failed to upload transaction attachment: {str(e)}")
