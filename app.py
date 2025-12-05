"""
Rättskoll OCR Test - Streamlit App
===================================
Main application for testing OCR on Swedish legal documents.
"""

import json
import time
from datetime import datetime

import streamlit as st

from config import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    UI_TEXT,
    MAX_FILE_SIZE_MB,
    REPLICATE_API_TOKEN,
    OUTPUT_DIR,
)
from models import OCRResult, ProcessingProgress
from pdf_processor import PDFProcessor, PDFProcessingError
from ocr_pipeline import OCRPipeline, OCRError


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Success/error badges */
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .error-badge {
        background-color: #dc3545;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Page expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
    }
    
    /* Stats cards */
    .stat-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE
# =============================================================================

if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None

if "processing" not in st.session_state:
    st.session_state.processing = False

if "progress" not in st.session_state:
    st.session_state.progress = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_time(seconds: float) -> str:
    """Format seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"


def create_download_json(result: OCRResult) -> str:
    """Create JSON string for download."""
    return json.dumps(result.to_export_dict(), ensure_ascii=False, indent=2)


def create_download_markdown(result: OCRResult) -> str:
    """Create Markdown string for download."""
    lines = [
        f"# OCR Resultat: {result.filename}",
        f"",
        f"**Bearbetat:** {result.processed_at.strftime('%Y-%m-%d %H:%M')}",
        f"**Antal sidor:** {result.total_pages}",
        f"**Lyckandegrad:** {result.success_rate:.0%}",
        f"**Bearbetningstid:** {format_time(result.processing_time)}",
        f"",
        "---",
        "",
    ]
    
    for page in result.pages:
        status = "✅" if page.success else "❌"
        lines.append(f"## Sida {page.page_number} {status}")
        lines.append("")
        
        if page.success:
            lines.append(page.text)
        else:
            lines.append(f"*Fel: {page.error}*")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # Header
    st.title(UI_TEXT["title"])
    st.markdown(f"*{UI_TEXT['subtitle']}*")
    st.divider()
    
    # Check API token
    if not REPLICATE_API_TOKEN:
        st.error(UI_TEXT["error_no_token"])
        st.info("""
        **Så här löser du detta:**
        1. Skapa ett konto på [replicate.com](https://replicate.com)
        2. Kopiera din API-token från [replicate.com/account](https://replicate.com/account)
        3. Skapa en `.env`-fil i projektmappen med:
        ```
        REPLICATE_API_TOKEN=r8_ditt_token_här
        ```
        4. Starta om appen
        """)
        return
    
    # File uploader
    uploaded_file = st.file_uploader(
        UI_TEXT["upload_label"],
        type=["pdf"],
        help=UI_TEXT["upload_help"],
    )
    
    # Process button
    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"Filen är för stor ({file_size_mb:.1f} MB). Max {MAX_FILE_SIZE_MB} MB.")
            return
        
        st.success(f"📄 **{uploaded_file.name}** ({file_size_mb:.1f} MB)")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            process_button = st.button("🚀 Starta OCR", type="primary", use_container_width=True)
        
        if process_button:
            process_document(uploaded_file)
    
    # Display results if available
    if st.session_state.ocr_result is not None:
        display_results(st.session_state.ocr_result)


def process_document(uploaded_file):
    """Process uploaded PDF through OCR pipeline."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Convert PDF to images
        status_text.text("📄 Konverterar PDF till bilder...")
        
        processor = PDFProcessor()
        images = processor.from_upload(uploaded_file)
        
        total_pages = len(images)
        status_text.text(f"📄 Hittade {total_pages} sidor. Startar OCR...")
        
        # Initialize OCR pipeline
        pipeline = OCRPipeline()
        
        # Process with progress updates
        def update_progress(progress: ProcessingProgress):
            progress_bar.progress(progress.progress_percent / 100)
            status_text.text(
                f"🔤 {progress.current_page_status} "
                f"({progress.current_page}/{progress.total_pages})"
            )
        
        result = pipeline.process_document(
            images=images,
            filename=uploaded_file.name,
            progress_callback=update_progress,
        )
        
        # Store result
        st.session_state.ocr_result = result
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Klar!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        st.rerun()
        
    except PDFProcessingError as e:
        st.error(f"❌ PDF-fel: {e}")
        progress_bar.empty()
        status_text.empty()
        
    except OCRError as e:
        st.error(f"❌ OCR-fel: {e}")
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"❌ Oväntat fel: {e}")
        progress_bar.empty()
        status_text.empty()


def display_results(result: OCRResult):
    """Display OCR results with statistics and page viewer."""
    
    st.divider()
    st.subheader(UI_TEXT["stats_title"])
    
    # Statistics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=UI_TEXT["total_pages"],
            value=result.total_pages
        )
    
    with col2:
        st.metric(
            label=UI_TEXT["success_rate"],
            value=f"{result.success_rate:.0%}"
        )
    
    with col3:
        st.metric(
            label=UI_TEXT["processing_time"],
            value=format_time(result.processing_time)
        )
    
    with col4:
        st.metric(
            label="Ord totalt",
            value=f"{result.total_words:,}"
        )
    
    # Download buttons
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        json_data = create_download_json(result)
        st.download_button(
            label=UI_TEXT["download_json"],
            data=json_data,
            file_name=f"{result.filename.replace('.pdf', '')}_ocr.json",
            mime="application/json",
            use_container_width=True,
        )
    
    with col2:
        md_data = create_download_markdown(result)
        st.download_button(
            label=UI_TEXT["download_md"],
            data=md_data,
            file_name=f"{result.filename.replace('.pdf', '')}_ocr.md",
            mime="text/markdown",
            use_container_width=True,
        )
    
    # Page viewer
    st.divider()
    st.subheader("📖 Sidvisning")
    
    # Page selector
    page_options = [f"Sida {p.page_number}" for p in result.pages]
    
    # View mode
    view_mode = st.radio(
        "Visningsläge",
        ["Alla sidor", "Välj sida"],
        horizontal=True,
    )
    
    if view_mode == "Välj sida":
        selected_page = st.selectbox(
            "Välj sida",
            range(1, result.total_pages + 1),
            format_func=lambda x: f"Sida {x}"
        )
        
        page = result.get_page(selected_page)
        if page:
            display_single_page(page)
    else:
        # Show all pages in expanders
        for page in result.pages:
            status_emoji = "✅" if page.success else "❌"
            word_info = f" ({page.word_count} ord)" if page.success else ""
            
            with st.expander(
                f"{status_emoji} Sida {page.page_number}{word_info}",
                expanded=page.page_number == 1
            ):
                display_single_page(page)


def display_single_page(page):
    """Display a single page's content."""
    
    if page.success:
        if page.has_content:
            # Show the markdown content
            st.markdown(page.text)
            
            # Show metadata
            with st.expander("📊 Sidmetadata"):
                st.write(f"**Bearbetningstid:** {page.processing_time:.1f}s")
                st.write(f"**Antal ord:** {page.word_count}")
                st.write(f"**Antal tecken:** {len(page.text)}")
        else:
            st.info("Sidan verkar vara tom eller innehåller väldigt lite text.")
    else:
        st.error(f"OCR misslyckades: {page.error}")


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.header("ℹ️ Om Rättskoll")
    st.markdown("""
    **Rättskoll OCR Test** är en testapplikation för att validera 
    OCR-extrahering av svenska förundersökningsprotokoll (FUP:ar).
    
    ### Hur det fungerar
    1. Ladda upp en PDF
    2. Varje sida konverteras till bild
    3. DeepSeek-OCR extraherar texten
    4. Resultatet visas med sidnummer
    
    ### Teknologi
    - **OCR:** DeepSeek-OCR via Replicate
    - **PDF:** pdf2image + Poppler
    - **UI:** Streamlit
    
    ### Nästa steg
    Efter denna testfas kommer vi bygga:
    - Extraheringsagent (personer, tider, platser)
    - Analysagenter (tidslinjekonflikter, motsägelser)
    - Rapportgenerator
    """)
    
    st.divider()
    
    if st.session_state.ocr_result:
        if st.button("🗑️ Rensa resultat"):
            st.session_state.ocr_result = None
            st.rerun()
    
    st.caption("Rättskoll v0.1 - OCR Test")


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    main()
