# 🔍 Rättskoll OCR Test

> **Phase 1** of the Rättskoll Forensic Auditor - Validating OCR on Swedish legal documents

## What is this?

This is a minimal test application to validate that we can accurately extract text from Swedish criminal investigation documents (FUPs - förundersökningsprotokoll) using DeepSeek-OCR.

**Why test first?** If OCR fails on Swedish legal documents, the entire forensic analysis system fails. This module validates the foundation before building the multi-agent analysis system.

## Quick Start

### Prerequisites

1. **Python 3.12+**
2. **Poppler** (for PDF processing):
   - Mac: `brew install poppler`
   - Ubuntu: `apt-get install poppler-utils`
   - Windows: [Download from GitHub](https://github.com/oschwartz10612/poppler-windows/releases)
3. **Replicate API Token** from [replicate.com](https://replicate.com)

### Installation

```bash
# Clone/download the project
cd rattskoll-ocr-test

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your REPLICATE_API_TOKEN
```

### Run the App

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Create Test Document (Optional)

If you don't have a real FUP to test with:

```bash
pip install reportlab  # Extra dependency for PDF creation
python create_sample_doc.py
```

This creates `test_docs/sample_fup.pdf` with mock Swedish legal content.

## Features

- ✅ PDF upload via web interface
- ✅ Page-by-page OCR processing
- ✅ Progress tracking during processing
- ✅ Swedish text support
- ✅ JSON export with page references
- ✅ Markdown export
- ✅ Error handling with retries

## Project Structure

```
rattskoll-ocr-test/
├── CLAUDE.md           # Knowledge base for Claude Code AI
├── README.md           # This file
├── app.py              # Streamlit main application
├── ocr_pipeline.py     # DeepSeek-OCR via Replicate
├── pdf_processor.py    # PDF → images conversion
├── models.py           # Pydantic data models
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
├── create_sample_doc.py # Test document generator
├── test_docs/          # Sample PDFs
└── outputs/            # Generated results
```

## How It Works

```
PDF Upload → Convert to Images → DeepSeek-OCR → Structured Results
                                      ↓
                              Replicate API
                        (lucataco/deepseek-ocr)
```

Each page is:
1. Converted to PNG image at 200 DPI
2. Base64 encoded for API
3. Processed by DeepSeek-OCR with "Convert to Markdown" mode
4. Stored with page number for citation tracking

## Configuration

Key settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `PDF_DPI` | 200 | Image quality (higher = better but slower) |
| `OCR_TASK_TYPE` | "Convert to Markdown" | Preserves document structure |
| `MAX_RETRIES` | 3 | Retry attempts per page |

## CLI Testing

Test individual components:

```bash
# Test PDF processor
python pdf_processor.py test_docs/sample.pdf

# Test full OCR pipeline
python ocr_pipeline.py test_docs/sample.pdf
```

## What's Next?

After validating OCR works reliably:

1. **Phase 2: Extraction Agent** - Parse OCR output into structured entities
2. **Phase 3: Analysis Workers** - Detect timeline conflicts, witness contradictions
3. **Phase 4: Full Pipeline** - LangGraph orchestration + report generation

## Troubleshooting

### "Poppler not installed"
Install Poppler for your OS (see Prerequisites above).

### "REPLICATE_API_TOKEN not set"
Create `.env` file with your token from [replicate.com/account](https://replicate.com/account).

### Slow processing
- Reduce `PDF_DPI` from 200 to 150
- Process fewer pages at once

### Swedish characters look wrong
DeepSeek-OCR handles Swedish natively. Check file encoding is UTF-8.

## License

MIT

---

*Part of the Rättskoll Project - AI Forensic Auditor for Swedish Criminal Investigations*
