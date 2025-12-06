"""
Rättskoll OCR Test - Configuration
===================================
Central configuration for OCR pipeline settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TEST_DOCS_DIR = PROJECT_ROOT / "test_docs"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
TEST_DOCS_DIR.mkdir(exist_ok=True)

# =============================================================================
# API CONFIGURATION
# =============================================================================

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not REPLICATE_API_TOKEN:
    print("⚠️  Warning: REPLICATE_API_TOKEN not set in environment")

if not GOOGLE_API_KEY:
    print("⚠️  Warning: GOOGLE_API_KEY not set in environment")

if not OPENROUTER_API_KEY:
    print("⚠️  Warning: OPENROUTER_API_KEY not set in environment")

# =============================================================================
# AVAILABLE PROVIDERS
# =============================================================================
PROVIDER_REPLICATE = "Replicate (DeepSeek)"
PROVIDER_GEMINI = "Google Gemini"

DEFAULT_PROVIDER = PROVIDER_GEMINI

# =============================================================================
# OCR SETTINGS
# =============================================================================

# -- Replicate / DeepSeek --
# DeepSeek-OCR model on Replicate
OCR_MODEL = "lucataco/deepseek-ocr:cb3b474fbfc56b1664c8c7841550bccecbe7b74c30e45ce938ffca1180b4dff5"
OCR_TASK_TYPE = "Convert to Markdown"
OCR_RESOLUTION = "Gundam (Recommended)"

# -- Google / Gemini --
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_SYSTEM_PROMPT = """You are an OCR specialist for Swedish legal documents (FUPs - förundersökningsprotokoll).
Extract ALL text from the image with these requirements:
- Preserve exact formatting including tables, headers, lists
- Use markdown format for structure
- Preserve Swedish characters (å, ä, ö) exactly
- For tables, use markdown table syntax
- Never summarize or interpret - extract verbatim
- If a page is blank, respond with only: [TOM SIDA]"""

GEMINI_GENERATION_CONFIG = {
    "temperature": 0.1,
    "max_output_tokens": 8192,
}

# -- OpenRouter / Claude --
CLAUDE_MODEL = "anthropic/claude-sonnet-4"  # OpenRouter model ID
CLAUDE_EXTRACTION_PROMPT = """Du är en juridisk expert som extraherar strukturerad information från svenska förundersökningsprotokoll (FUP:ar).

Analysera texten och extrahera:
1. **Tidshändelser** (TimelineEvent) - händelser med datum/tid och plats
2. **Personer** (Person) - namn och roll (misstänkt, vittne, målsägande, polis)
3. **Påståenden** (Claim) - faktapåståenden med källa

VIKTIGT:
- Bevara exakta sidnummer för alla citat
- Extrahera ENDAST information som explicit finns i texten
- Ange osäkerhet när datum/tid är otydliga
- Formatera som JSON enligt schemat"""

CLAUDE_EXTRACTION_CONFIG = {
    "temperature": 0.1,
    "max_tokens": 8192,
}

# =============================================================================
# PDF PROCESSING
# =============================================================================

# DPI for PDF to image conversion
# Higher = better quality but slower and larger images
# 200 is good balance, 300 for difficult scans
PDF_DPI = 200

# Image format for OCR
IMAGE_FORMAT = "PNG"

# =============================================================================
# PROCESSING LIMITS
# =============================================================================

# Maximum pages to process in one batch (prevents timeouts)
MAX_PAGES_PER_BATCH = 5

# Maximum retries for failed OCR attempts
MAX_RETRIES = 3

# Delay between retries (seconds) - will use exponential backoff
RETRY_BASE_DELAY = 2

# Timeout for single page OCR (seconds)
PAGE_TIMEOUT = 60

# Maximum file size for upload (MB)
MAX_FILE_SIZE_MB = 50

# =============================================================================
# UI SETTINGS
# =============================================================================

# Streamlit page config
PAGE_TITLE = "Rättskoll OCR Test"
PAGE_ICON = "🔍"
LAYOUT = "wide"

# Swedish UI text
UI_TEXT = {
    "title": "🔍 Rättskoll OCR Test",
    "subtitle": "Forensisk dokumentanalys för svenska förundersökningsprotokoll",
    "upload_label": "Ladda upp PDF (FUP)",
    "upload_help": "Ladda upp ett förundersökningsprotokoll i PDF-format",
    "processing": "Bearbetar dokument...",
    "page_label": "Sida",
    "success": "✅ Lyckades",
    "failed": "❌ Misslyckades",
    "download_json": "📥 Ladda ner resultat (JSON)",
    "download_md": "📥 Ladda ner resultat (Markdown)",
    "stats_title": "📊 Statistik",
    "total_pages": "Totalt antal sidor",
    "success_rate": "Lyckandegrad",
    "processing_time": "Bearbetningstid",
    "no_file": "Ingen fil uppladdad ännu",
    "error_no_token": "❌ API-nycklar saknas. Kontrollera .env-filen.",
    "select_provider": "Välj OCR-motor",
    # Page selection UI
    "page_count_info": "Dokumentet har {count} sidor",
    "page_selection_header": "Välj sidor",
    "page_range_label": "Sidintervall",
    "page_range_placeholder": "t.ex. 1-10, 15, 20-25",
    "page_range_help": "Ange sidor separerade med komma. Använd bindestreck för intervall. 'all' för alla sidor.",
    "show_thumbnails": "Visa miniatyrer",
    "thumbnail_loading": "Laddar miniatyrer...",
    "selected_pages": "{count} sidor valda",
    "export_pdf_btn": "Spara urval som PDF",
    "export_success": "PDF sparad: {path}",
    "download_selection_btn": "Ladda ner urval (PDF)",
    "invalid_range": "Ogiltigt sidintervall: {error}",
    "start_ocr_btn": "Starta OCR",
    "all_pages_btn": "Alla sidor",
    "first_10_btn": "Första 10",
    "export_header": "Exportera urval",
}

# =============================================================================
# LOGGING
# =============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def parse_page_range(range_str: str, max_page: int) -> list[int]:
    """
    Parse page range string into list of page numbers.

    Supports formats:
    - Single pages: "1, 5, 10"
    - Ranges: "1-10"
    - Mixed: "1-10, 15, 20-25"
    - "all" for all pages

    Args:
        range_str: User input string
        max_page: Maximum valid page number

    Returns:
        Sorted list of valid page numbers (1-indexed)

    Raises:
        ValueError: If format is invalid
    """
    if not range_str or not range_str.strip():
        raise ValueError("Inget sidintervall angivet")

    if range_str.strip().lower() == "all":
        return list(range(1, max_page + 1))

    pages = set()
    parts = range_str.replace(" ", "").split(",")

    for part in parts:
        if not part:
            continue
        if "-" in part:
            try:
                start_str, end_str = part.split("-", 1)
                start = int(start_str)
                end = int(end_str)
                if start > end:
                    start, end = end, start
                pages.update(range(start, end + 1))
            except ValueError:
                raise ValueError(f"Ogiltigt intervall: {part}")
        else:
            try:
                pages.add(int(part))
            except ValueError:
                raise ValueError(f"Ogiltigt sidnummer: {part}")

    # Filter to valid range
    valid_pages = sorted(p for p in pages if 1 <= p <= max_page)

    if not valid_pages:
        raise ValueError("Inga giltiga sidnummer hittades")

    return valid_pages
