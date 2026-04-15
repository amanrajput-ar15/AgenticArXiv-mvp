"""Gemini 2.5 Flash vision-based PDF page text extraction using google-genai SDK.

Key design decisions:
- Uses google-genai SDK (new unified SDK, not deprecated google-generativeai)
- Disk cache keyed by MD5 of the PNG file — never re-extracts the same page
- Low temperature (0.1) for factual extraction — reduces hallucination
- PIL Image objects passed directly — no manual base64 encoding needed
"""
import hashlib
import os
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Disk cache — saves cost and time on repeated ingestion of the same paper
CACHE_DIR = Path(os.getenv("VOLUME_PATH", "./data")) / "extraction_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

EXTRACTION_PROMPT = """Extract ALL text from this research paper page image.
Preserve:
- Section headers (prefix with ##)
- Figure captions (prefix with [FIGURE:])
- Table content (use | separator for columns)
- Mathematical notation (LaTeX-like notation)
- Reading order: top-to-bottom, respecting multi-column layout

Return only extracted text. No commentary, no preamble."""


def _cache_key(image_path: str) -> str:
    """MD5 of the raw file bytes — stable cache key across runs."""
    with open(image_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def extract_page(image_path: str) -> str:
    """Extract text from a single PDF page image using Gemini 2.5 Flash vision.

    Results are cached to disk by file hash — identical pages are extracted once.
    """
    key = _cache_key(image_path)
    cache_file = CACHE_DIR / f"{key}.txt"

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    image = Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[EXTRACTION_PROMPT, image],
        config=types.GenerateContentConfig(
            temperature=0.1,  # factual extraction — low temp
            max_output_tokens=2048,
        ),
    )
    text = response.text
    cache_file.write_text(text, encoding="utf-8")
    return text


def extract_pdf_text(image_paths: list[str]) -> str:
    """Extract text from all pages of a PDF.

    Args:
        image_paths: Ordered list of PNG paths, one per page.

    Returns:
        Concatenated structured text with page separators.
    """
    pages = []
    for i, path in enumerate(image_paths):
        try:
            page_text = extract_page(path)
            pages.append(f"--- PAGE {i + 1} ---\n{page_text}")
        except Exception as e:
            pages.append(f"--- PAGE {i + 1} --- [extraction failed: {e}]")
    return "\n\n".join(pages)