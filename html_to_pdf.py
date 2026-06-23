#!/usr/bin/env python3
"""
html_to_pdf.py — Convert HTML files to pixel-perfect PDFs using Playwright.

Usage:
    python html_to_pdf.py <html_path> [pdf_path]
    python html_to_pdf.py --batch <directory> [--output <output_dir>]

If pdf_path is not provided, generates PDF in the same directory.

Rules:
    - The HTML file should be the final reviewed version.
    - PDF = faithful replica of HTML. Playwright doesn't alter layout.
    - No format, size, or margin parameters. CSS controls everything.
    - Mermaid.js diagrams render automatically (3-second wait for async rendering).

Requirements:
    - Python 3.10+
    - Playwright: pip install playwright && playwright install chromium

CSS Guidelines (in your HTML):
    @page { margin: 0; }
    body { max-width: 210mm; margin: 0 auto; padding: 14mm; }
    .section { page-break-before: always; }
    .block { page-break-inside: avoid; }
    h2, h3 { page-break-after: avoid; }
"""

import sys
import os
import glob
import argparse
import shutil
import tempfile


def html_to_pdf(html_path, pdf_path=None, wait_ms=3000, safe_mode=False):
    """Convert a single HTML file to PDF.
    
    Args:
        html_path: Path to the HTML file.
        pdf_path: Output PDF path. If None, uses same directory with .pdf extension.
        wait_ms: Milliseconds to wait for async rendering (Mermaid.js, fonts). Default: 3000.
        safe_mode: If True, copies HTML to a temp directory first (avoids path encoding issues).
    
    Returns:
        Path to the generated PDF.
    """
    if not os.path.isfile(html_path):
        print(f"ERROR: file not found: {html_path}")
        sys.exit(1)

    if pdf_path is None:
        pdf_path = os.path.splitext(html_path)[0] + ".pdf"

    from playwright.sync_api import sync_playwright

    source_path = html_path
    tmp_dir = None

    if safe_mode:
        tmp_dir = tempfile.mkdtemp(prefix="html2pdf_")
        base_dir = os.path.dirname(html_path)
        shutil.copy2(html_path, os.path.join(tmp_dir, "doc.html"))
        # Copy sibling assets (images, CSS) to temp dir
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.svg", "*.css", "*.gif", "*.webp"):
            for asset in glob.glob(os.path.join(base_dir, ext)):
                shutil.copy2(asset, tmp_dir)
        source_path = os.path.join(tmp_dir, "doc.html")

    try:
        file_url = "file:///" + source_path.replace("\\", "/")

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(file_url)
            page.wait_for_timeout(wait_ms)
            page.pdf(
                path=pdf_path,
                print_background=True,
                prefer_css_page_size=True,
            )
            browser.close()
    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)

    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"✓ {os.path.basename(pdf_path)} ({size_kb:.1f} KB)")
    return pdf_path


def batch_convert(input_dir, output_dir=None, wait_ms=3000):
    """Convert all HTML files in a directory to PDF.
    
    Args:
        input_dir: Directory containing HTML files.
        output_dir: Output directory for PDFs. If None, saves alongside HTML files.
        wait_ms: Milliseconds to wait for async rendering per file.
    
    Returns:
        List of generated PDF paths.
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    html_files = sorted(glob.glob(os.path.join(input_dir, "*.html")))
    if not html_files:
        print(f"No HTML files found in: {input_dir}")
        return []

    print(f"Converting {len(html_files)} files...")
    results = []

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for html_file in html_files:
            name = os.path.splitext(os.path.basename(html_file))[0]
            if output_dir:
                pdf_path = os.path.join(output_dir, f"{name}.pdf")
            else:
                pdf_path = os.path.splitext(html_file)[0] + ".pdf"

            file_url = "file:///" + html_file.replace("\\", "/")
            page.goto(file_url)
            page.wait_for_timeout(wait_ms)
            page.pdf(
                path=pdf_path,
                print_background=True,
                prefer_css_page_size=True,
            )
            size_kb = os.path.getsize(pdf_path) / 1024
            print(f"  ✓ {name}.pdf ({size_kb:.1f} KB)")
            results.append(pdf_path)

        browser.close()

    print(f"\nDone: {len(results)} PDFs generated.")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HTML to pixel-perfect PDF using Playwright")
    parser.add_argument("input", help="HTML file path, or directory (with --batch)")
    parser.add_argument("output", nargs="?", help="Output PDF path (single) or directory (batch)")
    parser.add_argument("--batch", action="store_true", help="Convert all HTML files in the input directory")
    parser.add_argument("--wait", type=int, default=3000, help="Wait time in ms for async rendering (default: 3000)")
    parser.add_argument("--safe", action="store_true", help="Use temp directory to avoid path encoding issues")
    args = parser.parse_args()

    if args.batch:
        batch_convert(args.input, args.output, args.wait)
    else:
        html_to_pdf(args.input, args.output, args.wait, args.safe)
