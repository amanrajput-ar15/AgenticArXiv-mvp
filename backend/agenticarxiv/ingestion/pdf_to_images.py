"""Thin wrapper over pdf2image.convert_from_path.

Converts each page of a PDF to a PNG file at the given DPI.
Requires poppler at system level:
  - Mac:    brew install poppler
  - Ubuntu: apt install poppler-utils
  - Railway: nixpacks.toml handles this (nixPkgs = ["poppler_utils"])
"""
from pathlib import Path
from pdf2image import convert_from_path


def pdf_to_images(
    pdf_path: str,
    output_dir: str,
    dpi: int = 150,
) -> list[str]:
    """Convert a PDF to a list of PNG image paths.

    Args:
        pdf_path:   Absolute path to the PDF file.
        output_dir: Directory where page PNGs will be written.
        dpi:        Resolution for rendering (150 = good quality/cost balance).

    Returns:
        Sorted list of absolute paths to the generated PNG files.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    convert_from_path(
        str(pdf_path),
        dpi=dpi,
        output_folder=str(output_path),
        fmt="png",
        output_file="page",
    )

    # pdf2image names files like page0001-1.ppm or page-1.png depending on version
    # Glob both patterns and sort deterministically
    images = sorted(output_path.glob("*.png"))
    return [str(p) for p in images]