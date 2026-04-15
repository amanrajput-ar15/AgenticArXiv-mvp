"""arXiv paper fetcher — search by query or download by ID.

Uses the public arXiv REST API (no auth required).
Returns structured paper metadata + downloads PDF to disk.
"""
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ARXIV_API  = "http://export.arxiv.org/api/query"
ARXIV_PDF  = "https://arxiv.org/pdf"
NS         = {"atom": "http://www.w3.org/2005/Atom",
               "arxiv": "http://arxiv.org/schemas/atom"}


def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """Search arXiv and return structured paper metadata.

    Args:
        query:       Full-text search string.
        max_results: Number of papers to return (max 100).

    Returns:
        List of dicts with keys: arxiv_id, title, authors, published, abstract, pdf_url.
    """
    resp = requests.get(ARXIV_API, params={
        "search_query": f"all:{query}",
        "start":        0,
        "max_results":  max_results,
        "sortBy":       "relevance",
    }, timeout=30)
    resp.raise_for_status()

    root    = ET.fromstring(resp.text)
    papers  = []

    for entry in root.findall("atom:entry", NS):
        arxiv_id = entry.find("atom:id", NS).text.split("/abs/")[-1]
        title    = entry.find("atom:title", NS).text.strip().replace("\n", " ")
        published = (entry.find("atom:published", NS).text or "")[:10]
        authors  = [
            a.find("atom:name", NS).text
            for a in entry.findall("atom:author", NS)
        ]
        abstract = (entry.find("atom:summary", NS).text or "").strip()

        papers.append({
            "arxiv_id":  arxiv_id,
            "title":     title,
            "authors":   authors,
            "published": published,
            "abstract":  abstract,
            "pdf_url":   f"{ARXIV_PDF}/{arxiv_id}.pdf",
        })

    return papers


def download_pdf(arxiv_id: str, dest_dir: str) -> str:
    """Download a paper PDF by arXiv ID.

    Args:
        arxiv_id: e.g. "2312.00001" or "2312.00001v2"
        dest_dir: Directory to save the PDF.

    Returns:
        Absolute path to the downloaded PDF file.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    url      = f"{ARXIV_PDF}/{arxiv_id}.pdf"
    out_path = dest / f"{arxiv_id.replace('/', '_')}.pdf"

    resp = requests.get(url, timeout=60, stream=True)
    resp.raise_for_status()

    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return str(out_path)