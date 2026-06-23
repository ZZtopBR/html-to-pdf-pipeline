# html-to-pdf-pipeline

Playwright-based HTML to PDF converter with CSS page break support, Mermaid.js rendering, and batch conversion.

Battle-tested on **100+ documents** — stakeholder reports, user stories with app mockups, technical specs with Mermaid diagrams.

## Why This Exists

Most HTML-to-PDF tools fight your CSS. They inject their own margins, ignore page breaks, and mangle complex layouts. This tool does one thing: it opens your HTML in Chromium and prints it exactly as the browser renders it.

**The browser is the renderer. CSS is the layout engine. Playwright just captures it.**

## Features

- **Pixel-perfect output** — what you see in the browser is what you get in the PDF
- **CSS-controlled layout** — page breaks, margins, typography via standard CSS
- **Mermaid.js support** — diagrams render automatically (async wait built-in)
- **Batch conversion** — convert an entire directory of HTML files in one command
- **Safe mode** — temp directory isolation for paths with special characters
- **Minimal dependencies** — just Playwright

## Install

```bash
pip install playwright
playwright install chromium
```

## Usage

### Single file

```bash
python html_to_pdf.py report.html
python html_to_pdf.py report.html output/report.pdf
```

### Batch conversion

```bash
python html_to_pdf.py --batch ./html_files/
python html_to_pdf.py --batch ./html_files/ --output ./pdfs/
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--batch` | off | Convert all HTML files in directory |
| `--output` | same dir | Output directory for PDFs |
| `--wait` | 3000 | Wait time (ms) for async rendering (Mermaid.js, fonts) |
| `--safe` | off | Copy to temp dir first (fixes path encoding issues) |

### As a library

```python
from html_to_pdf import html_to_pdf, batch_convert

# Single file
html_to_pdf("report.html", "output.pdf")

# With extra wait for heavy Mermaid diagrams
html_to_pdf("complex.html", wait_ms=5000)

# Batch
batch_convert("./html_files/", "./pdfs/")
```

## CSS Recipe

For best results, use this CSS pattern in your HTML files:

```css
@page { margin: 0; }

body {
    max-width: 210mm;
    margin: 0 auto;
    padding: 14mm;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Force page breaks between sections */
.section { page-break-before: always; }

/* Keep blocks together */
.block { page-break-inside: avoid; }

/* Prevent orphaned headings */
h2, h3 { page-break-after: avoid; }
```

**Key rule:** Set `@page { margin: 0 }` and control everything with CSS `padding`. Never pass `margin` or `format` to Playwright — let CSS do its job.

## Mermaid.js Support

Include Mermaid via CDN in your HTML. It renders in the browser before Playwright captures:

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true, theme: 'neutral' });</script>

<div class="mermaid">
    flowchart TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Action]
</div>
```

The default 3-second wait handles most diagrams. For pages with 5+ Mermaid blocks, use `--wait 5000`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Passing `margin` to Playwright | Use CSS `padding` + `@page { margin: 0 }` |
| Passing `format="A4"` | Use `prefer_css_page_size=True` only |
| Using `min-height` on page divs | Remove — causes blank pages |
| Heading alone at page bottom | Wrap heading + content in `<div class="block">` |
| Mermaid shows raw text | Increase `--wait` (async rendering needs time) |
| `print_background=False` | Always `True` — otherwise gradients/colors vanish |

## License

MIT
