import base64
import io

import httpx
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader


def extract_policy_text(input_type: str, raw_content: str) -> str:
    if input_type == "url":
        return _extract_from_url(raw_content)
    elif input_type == "pdf":
        return _extract_from_pdf(raw_content)
    return raw_content


def _extract_from_url(url: str) -> str:
    resp = httpx.get(url, timeout=15, follow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Try to find main content
    main = soup.find("main") or soup.find("article") or soup.find("body")
    if main is None:
        raise ValueError("Could not extract text from URL")

    text = main.get_text(separator="\n", strip=True)
    # Clean up excessive whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)[:20_000]


def _extract_from_pdf(base64_content: str) -> str:
    pdf_bytes = base64.b64decode(base64_content)
    reader = PdfReader(io.BytesIO(pdf_bytes))

    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)

    return "\n".join(text_parts)[:20_000]
