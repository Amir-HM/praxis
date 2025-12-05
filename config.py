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

if not REPLICATE_API_TOKEN:
    print("⚠️  Warning: REPLICATE_API_TOKEN not set in environment")

# =============================================================================
# OCR SETTINGS
# =============================================================================

# DeepSeek-OCR model on Replicate
OCR_MODEL = "lucataco/deepseek-ocr:cb3b474fbfc56b1664c8c7841550bccecbe7b74c30e45ce938ffca1180b4dff5"

# Task type: "Convert to Markdown" preserves structure (tables, headings)
# Options: "Convert to Markdown", "Free OCR", "Locate Object by Reference"
OCR_TASK_TYPE = "Convert to Markdown"

# Resolution: "Gundam (Recommended)" for best accuracy
# Options: "Gundam (Recommended)", "Ranger"
OCR_RESOLUTION = "Gundam (Recommended)"

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
    "error_no_token": "❌ REPLICATE_API_TOKEN saknas. Lägg till i .env-fil.",
}

# =============================================================================
# LOGGING
# =============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
