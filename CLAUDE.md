# RÄTTSKOLL OCR MODULE - Claude Code Knowledge Base

> **Project:** Rättskoll - AI Forensic Auditor for Swedish Criminal Investigations
> **Module:** OCR Pipeline Test App
> **Status:** Phase 1 - Foundation Build
> **Priority:** Validate OCR before building multi-agent system

---

## 🎯 MISSION

Build a minimal OCR test app that proves we can accurately extract text from Swedish criminal investigation documents (FUPs - förundersökningsprotokoll). This is the foundation for Rättskoll's forensic analysis system.

**Why this matters:** Wrongful convictions happen because critical contradictions get buried in 1,000+ page documents. If OCR fails, the entire system fails.

---

## 📁 PROJECT STRUCTURE

```
rattskoll-ocr-test/
├── CLAUDE.md              # THIS FILE - Knowledge base for Claude Code
├── app.py                 # Streamlit main application
├── ocr_pipeline.py        # DeepSeek-OCR wrapper via Replicate
├── pdf_processor.py       # PDF → images conversion
├── models.py              # Pydantic data models
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .env                   # API keys (gitignored)
├── test_docs/             # Sample PDFs for testing
│   └── sample_fup.pdf
└── outputs/               # Generated results
    └── .gitkeep
```

---

## 🔧 TECH STACK

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Streamlit | Rapid prototyping UI |
| OCR | DeepSeek-OCR via Replicate | Document → Markdown |
| PDF Processing | pdf2image + Pillow | PDF → Images |
| Data Models | Pydantic v2 | Structured validation |
| Language | Python 3.12+ | Runtime |

---

## 🔑 API REFERENCE

### DeepSeek-OCR via Replicate

**Model:** `lucataco/deepseek-ocr`

**Input Parameters:**
```python
{
    "image": str,              # URL or base64 data URI (REQUIRED)
    "task_type": str,          # See options below (optional)
    "resolution_size": str,    # "Gundam (Recommended)" | "Ranger" (optional)
    "reference_text": str      # For locate task only (optional)
}
```

**Task Types:**
- `"Convert to Markdown"` ← **USE THIS** for FUPs (preserves tables, structure)
- `"Free OCR"` - Raw text extraction only
- `"Locate Object by Reference"` - Find specific text in image

**Resolution Sizes:**
- `"Gundam (Recommended)"` ← **USE THIS** - Best accuracy
- `"Ranger"` - Faster but less accurate

**Output:** String containing markdown text. With grounding mode includes bounding boxes:
```
<|ref|>text<|/ref|><|det|>[[130, 72, 624, 97]]<|/det|>
## Actual content here
```

**API Call Pattern:**
```python
import replicate

output = replicate.run(
    "lucataco/deepseek-ocr",
    input={
        "image": "data:image/png;base64,{base64_string}",
        "task_type": "Convert to Markdown",
        "resolution_size": "Gundam (Recommended)"
    }
)
# output is a string
```

---

## 📋 DATA MODELS

### OCRPage
```python
class OCRPage(BaseModel):
    page_number: int          # 1-indexed page number
    text: str                 # Extracted markdown text
    success: bool             # Whether OCR succeeded
    error: str | None = None  # Error message if failed
    processing_time: float    # Seconds to process
```

### OCRResult
```python
class OCRResult(BaseModel):
    filename: str
    total_pages: int
    pages: list[OCRPage]
    processing_time: float    # Total time
    success_rate: float       # Percentage of pages that succeeded
```

---

## ⚙️ CONFIGURATION

### Environment Variables (.env)
```bash
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Constants (config.py)
```python
OCR_MODEL = "lucataco/deepseek-ocr"
TASK_TYPE = "Convert to Markdown"
RESOLUTION = "Gundam (Recommended)"
PDF_DPI = 200                    # Balance quality/speed
MAX_PAGES_PER_BATCH = 5          # Prevent timeouts
MAX_RETRIES = 3                  # Retry failed pages
RETRY_DELAY = 2                  # Seconds between retries
```

---

## 🔄 CORE WORKFLOWS

### 1. PDF Upload → OCR → Display

```
User uploads PDF
       ↓
pdf_processor.pdf_to_images()
       ↓
For each image:
    ocr_pipeline.ocr_page()
       ↓
Aggregate results
       ↓
Display in Streamlit with page navigation
       ↓
Option to download JSON
```

### 2. Single Page OCR Flow

```
PIL Image
    ↓
Convert to base64 PNG
    ↓
Call Replicate API
    ↓
Parse response
    ↓
Return OCRPage with page_number preserved
```

---

## 🚨 ERROR HANDLING

| Error | Cause | Solution |
|-------|-------|----------|
| `ReplicateError` | API timeout/rate limit | Retry with exponential backoff |
| Blank output | Blank page or image issue | Mark as success with empty text |
| Garbled text | Low quality scan | Increase DPI to 300 |
| Timeout | Large/complex page | Reduce resolution or skip |

### Retry Pattern
```python
import time

def ocr_with_retry(image, page_num, max_retries=3):
    for attempt in range(max_retries):
        try:
            return ocr_page(image, page_num)
        except Exception as e:
            if attempt == max_retries - 1:
                return OCRPage(
                    page_number=page_num,
                    text="",
                    success=False,
                    error=str(e),
                    processing_time=0
                )
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## ✅ ACCEPTANCE CRITERIA

### MVP (Phase 1)
- [ ] Upload PDF via Streamlit file uploader
- [ ] Convert PDF to images (all pages)
- [ ] Process each page through DeepSeek-OCR
- [ ] Display extracted text with page numbers
- [ ] Show progress during processing
- [ ] Download results as JSON
- [ ] Handle errors gracefully (don't crash on bad pages)
- [ ] Process 10+ page document successfully

### Quality Gates
- Single page OCR: < 15 seconds
- 10-page document: < 3 minutes
- Swedish text accuracy: Readable (manual verification)
- No data loss: All pages accounted for

---

## 🧪 TESTING

### Manual Test Cases

1. **Simple Document**
   - Upload 1-2 page typed PDF
   - Verify text extraction is accurate
   - Check page numbers preserved

2. **Multi-page Document**
   - Upload 10+ page PDF
   - Verify all pages processed
   - Check progress updates correctly

3. **Scanned Document**
   - Upload scanned/image PDF
   - Verify OCR handles it
   - Check Swedish characters (å, ä, ö)

4. **Edge Cases**
   - Blank page handling
   - Mixed text/image pages
   - Tables and structured content

### Test Command
```bash
streamlit run app.py
# Then upload test_docs/sample_fup.pdf
```

---

## 📊 OUTPUT FORMAT

### JSON Export Structure
```json
{
  "filename": "fup_case_2025.pdf",
  "total_pages": 15,
  "processing_time": 120.5,
  "success_rate": 0.93,
  "pages": [
    {
      "page_number": 1,
      "text": "# FÖRUNDERSÖKNINGSPROTOKOLL\n\nMålnummer: B 1234-25...",
      "success": true,
      "error": null,
      "processing_time": 8.2
    },
    {
      "page_number": 2,
      "text": "## VITTNESFÖRHÖR\n\nFörhöret hållet: 2025-01-16...",
      "success": true,
      "error": null,
      "processing_time": 7.8
    }
  ]
}
```

---

## 🔮 WHAT COMES NEXT

After Phase 1 OCR validation:

### Phase 2: Structured Extraction
- Parse markdown into entities (TimelineEvent, Person, Claim, Evidence)
- Use Claude API for intelligent extraction
- Preserve page citations

### Phase 3: Analysis Workers
- Timeline conflict detection (algorithmic)
- Witness contradiction detection (embeddings + LLM)
- Evidence gap analysis

### Phase 4: Full Pipeline
- LangGraph multi-agent orchestration
- PDF report generation
- Production deployment

---

## 🐛 COMMON ISSUES & FIXES

### "ModuleNotFoundError: pdf2image"
```bash
pip install pdf2image
# Also need poppler:
# Mac: brew install poppler
# Ubuntu: apt-get install poppler-utils
# Windows: Download from poppler releases
```

### "REPLICATE_API_TOKEN not set"
```bash
# Create .env file with:
REPLICATE_API_TOKEN=r8_your_token_here

# Or export directly:
export REPLICATE_API_TOKEN=r8_your_token_here
```

### "Timeout processing page"
- Reduce `PDF_DPI` from 200 to 150
- Or increase timeout in Replicate client
- Or process in smaller batches

### "Swedish characters look wrong"
- DeepSeek handles Swedish natively
- Check file is saved with UTF-8 encoding
- Verify font in Streamlit supports Swedish

---

## 📝 CODE STYLE

- Use type hints everywhere
- Pydantic models for all data structures
- Async where beneficial (future-proofing)
- Clear error messages in Swedish context
- Document page number preservation logic

---

## 🚀 QUICK START

```bash
# 1. Clone/create project
cd rattskoll-ocr-test

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your REPLICATE_API_TOKEN

# 5. Run the app
streamlit run app.py
```

---

## 📚 REFERENCES

- [DeepSeek-OCR on Replicate](https://replicate.com/lucataco/deepseek-ocr)
- [DeepSeek-OCR Paper](https://github.com/deepseek-ai/DeepSeek-OCR/blob/main/DeepSeek_OCR_paper.pdf)
- [Replicate Python Client](https://github.com/replicate/replicate-python)
- [Streamlit Docs](https://docs.streamlit.io/)
- [pdf2image Docs](https://pdf2image.readthedocs.io/)

---

*Last updated: December 2025*
*Module: OCR Test App - Phase 1*
*Parent Project: Rättskoll Forensic Auditor*
