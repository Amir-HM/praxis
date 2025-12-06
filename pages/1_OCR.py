"""
Rättskoll - OCR Page
====================
Upload and process PDF documents with OCR.
"""

import json
import time
from pathlib import Path

import streamlit as st

from datetime import datetime

from config import (
    UI_TEXT,
    MAX_FILE_SIZE_MB,
    REPLICATE_API_TOKEN,
    GOOGLE_API_KEY,
    PROVIDER_REPLICATE,
    PROVIDER_GEMINI,
    DEFAULT_PROVIDER,
    OUTPUT_DIR,
    parse_page_range,
)
from models import OCRResult, OCRPage, ProcessingProgress
from pdf_processor import PDFProcessor, PDFProcessingError
from pdf_exporter import PDFExporter, PDFExportError
from ocr_pipeline import OCRPipeline, OCRError


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="OCR - Rättskoll",
    page_icon="📄",
    layout="wide",
)


# =============================================================================
# SESSION STATE
# =============================================================================

if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if "total_page_count" not in st.session_state:
    st.session_state.total_page_count = 0

if "selected_pages" not in st.session_state:
    st.session_state.selected_pages = []

if "thumbnails" not in st.session_state:
    st.session_state.thumbnails = {}

if "original_filename" not in st.session_state:
    st.session_state.original_filename = ""

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None


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


def save_ocr_result(result: OCRResult) -> Path:
    """Save OCR result to outputs/ directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(result.filename).stem
    output_path = OUTPUT_DIR / f"{base_name}_ocr_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.to_export_dict(), f, ensure_ascii=False, indent=2)

    return output_path


def load_ocr_result(json_path: Path) -> OCRResult:
    """Load OCR result from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reconstruct OCRResult from dict
    pages = [
        OCRPage(
            page_number=p["page_number"],
            text=p["text"],
            success=p["success"],
            error=p.get("error"),
            processing_time=p.get("processing_time", 0.0),
        )
        for p in data["pages"]
    ]

    return OCRResult(
        filename=data["filename"],
        total_pages=data["total_pages"],
        pages=pages,
        processing_time=data.get("processing_time", 0.0),
    )


def load_ocr_from_uploaded_json(uploaded_file) -> OCRResult:
    """Load OCR result from uploaded JSON file."""
    data = json.load(uploaded_file)

    pages = [
        OCRPage(
            page_number=p["page_number"],
            text=p["text"],
            success=p["success"],
            error=p.get("error"),
            processing_time=p.get("processing_time", 0.0),
        )
        for p in data["pages"]
    ]

    return OCRResult(
        filename=data["filename"],
        total_pages=data["total_pages"],
        pages=pages,
        processing_time=data.get("processing_time", 0.0),
    )


def get_saved_ocr_files() -> list[Path]:
    """Get list of saved OCR result files."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    return sorted(OUTPUT_DIR.glob("*_ocr_*.json"), reverse=True)


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


def reset_session_for_new_upload():
    """Clear session state when new PDF is uploaded."""
    st.session_state.pdf_bytes = None
    st.session_state.total_page_count = 0
    st.session_state.selected_pages = []
    st.session_state.thumbnails = {}
    st.session_state.ocr_result = None


def page_selection_ui(uploaded_file) -> list[int] | None:
    """Display page selection UI after upload."""
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.last_uploaded_file != current_file_id:
        reset_session_for_new_upload()
        st.session_state.last_uploaded_file = current_file_id

    if st.session_state.pdf_bytes is None:
        st.session_state.pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        st.session_state.original_filename = uploaded_file.name

    if st.session_state.total_page_count == 0:
        processor = PDFProcessor()
        st.session_state.total_page_count = processor.get_page_count_from_bytes(
            st.session_state.pdf_bytes
        )

    total_pages = st.session_state.total_page_count

    st.info(UI_TEXT["page_count_info"].format(count=total_pages))

    st.subheader(UI_TEXT["page_selection_header"])

    col1, col2 = st.columns([3, 1])

    with col1:
        default_value = "all" if total_pages <= 20 else "1-10"
        page_range_input = st.text_input(
            UI_TEXT["page_range_label"],
            value=default_value,
            placeholder=UI_TEXT["page_range_placeholder"],
            help=UI_TEXT["page_range_help"],
            key="page_range_input",
        )

        try:
            selected = parse_page_range(page_range_input, total_pages)
            st.session_state.selected_pages = selected
            st.success(UI_TEXT["selected_pages"].format(count=len(selected)))
        except ValueError as e:
            st.error(UI_TEXT["invalid_range"].format(error=str(e)))
            return None

    with col2:
        st.write("")
        st.write("")
        if st.button(UI_TEXT["all_pages_btn"], use_container_width=True):
            st.session_state.selected_pages = list(range(1, total_pages + 1))
            st.rerun()
        if st.button(UI_TEXT["first_10_btn"], use_container_width=True):
            st.session_state.selected_pages = list(range(1, min(11, total_pages + 1)))
            st.rerun()

    with st.expander(UI_TEXT["show_thumbnails"], expanded=False):
        display_thumbnail_grid(total_pages)

    st.divider()
    display_pdf_export_options()

    return st.session_state.selected_pages if st.session_state.selected_pages else None


def display_thumbnail_grid(total_pages: int):
    """Display thumbnail preview grid."""
    MAX_THUMBNAILS = 50

    if total_pages > MAX_THUMBNAILS:
        thumb_range = st.text_input(
            f"Visa miniatyrer för sidor (max {MAX_THUMBNAILS})",
            value="1-50",
            key="thumb_range"
        )
        try:
            thumb_pages = parse_page_range(thumb_range, total_pages)[:MAX_THUMBNAILS]
        except ValueError:
            thumb_pages = list(range(1, min(MAX_THUMBNAILS + 1, total_pages + 1)))
    else:
        thumb_pages = list(range(1, total_pages + 1))

    missing = [p for p in thumb_pages if p not in st.session_state.thumbnails]

    if missing:
        with st.spinner(UI_TEXT["thumbnail_loading"]):
            processor = PDFProcessor()
            new_thumbs = processor.generate_thumbnails(
                st.session_state.pdf_bytes,
                missing,
                thumbnail_dpi=50
            )
            st.session_state.thumbnails.update(new_thumbs)

    cols = st.columns(5)
    selected_pages = set(st.session_state.selected_pages)

    for i, page_num in enumerate(thumb_pages):
        col = cols[i % 5]
        with col:
            thumb = st.session_state.thumbnails.get(page_num)
            if thumb:
                indicator = "✓ " if page_num in selected_pages else ""
                st.image(
                    thumb,
                    caption=f"{indicator}Sida {page_num}",
                    use_container_width=True,
                )


def display_pdf_export_options():
    """Display PDF export buttons."""
    if not st.session_state.selected_pages:
        return

    st.subheader(UI_TEXT["export_header"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button(UI_TEXT["export_pdf_btn"], type="secondary", use_container_width=True):
            try:
                exporter = PDFExporter()
                output_path = exporter.save_to_file(
                    st.session_state.pdf_bytes,
                    st.session_state.selected_pages,
                    st.session_state.original_filename,
                )
                st.success(UI_TEXT["export_success"].format(path=output_path))
            except PDFExportError as e:
                st.error(f"Export misslyckades: {e}")

    with col2:
        try:
            exporter = PDFExporter()
            pdf_data = exporter.extract_pages(
                st.session_state.pdf_bytes,
                st.session_state.selected_pages,
            )

            base_name = Path(st.session_state.original_filename).stem
            download_name = f"{base_name}_urval.pdf"

            st.download_button(
                label=UI_TEXT["download_selection_btn"],
                data=pdf_data,
                file_name=download_name,
                mime="application/pdf",
                use_container_width=True,
            )
        except PDFExportError as e:
            st.error(f"Kunde inte skapa nedladdning: {e}")


def process_document_selected(uploaded_file, provider: str, selected_pages: list[int]):
    """Process only selected pages through OCR pipeline."""
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("📄 Konverterar valda sidor till bilder...")

        processor = PDFProcessor()
        page_images = processor.from_bytes_selected(
            st.session_state.pdf_bytes,
            selected_pages
        )

        status_text.text(f"📄 Konverterade {len(page_images)} sidor. Startar OCR med {provider}...")

        pipeline = OCRPipeline(provider=provider)

        pages_result = []
        total = len(page_images)
        start_time = time.time()

        for i, (page_num, image) in enumerate(page_images):
            progress_bar.progress((i + 1) / total)
            status_text.text(f"🔤 Bearbetar sida {page_num}... ({i+1}/{total})")

            page_result = pipeline.ocr_single_page(image, page_num)
            pages_result.append(page_result)

        total_time = time.time() - start_time

        result = OCRResult(
            filename=uploaded_file.name,
            total_pages=len(selected_pages),
            pages=pages_result,
            processing_time=total_time,
        )

        st.session_state.ocr_result = result

        # Auto-save OCR result
        try:
            saved_path = save_ocr_result(result)
            status_text.text(f"✅ Klar! Sparad till: {saved_path.name}")
        except Exception:
            status_text.text("✅ Klar!")

        progress_bar.progress(100)
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
    """Display OCR results with statistics."""
    st.divider()
    st.subheader(UI_TEXT["stats_title"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label=UI_TEXT["total_pages"], value=result.total_pages)

    with col2:
        st.metric(label=UI_TEXT["success_rate"], value=f"{result.success_rate:.0%}")

    with col3:
        st.metric(label=UI_TEXT["processing_time"], value=format_time(result.processing_time))

    with col4:
        st.metric(label="Ord totalt", value=f"{result.total_words:,}")

    st.divider()
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

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

    with col3:
        if st.button("💾 Spara lokalt", use_container_width=True, help="Spara till outputs/ mappen"):
            try:
                saved_path = save_ocr_result(result)
                st.success(f"Sparat: {saved_path.name}")
            except Exception as e:
                st.error(f"Kunde inte spara: {e}")

    st.divider()
    st.subheader("📖 Sidvisning")

    view_mode = st.radio(
        "Visningsläge",
        ["Alla sidor", "Välj sida"],
        horizontal=True,
    )

    if view_mode == "Välj sida":
        page_numbers = [p.page_number for p in result.pages]
        selected_page = st.selectbox(
            "Välj sida",
            page_numbers,
            format_func=lambda x: f"Sida {x}"
        )

        page = result.get_page(selected_page)
        if page:
            display_single_page(page)
    else:
        for page in result.pages:
            status_emoji = "✅" if page.success else "❌"
            word_info = f" ({page.word_count} ord)" if page.success else ""

            with st.expander(
                f"{status_emoji} Sida {page.page_number}{word_info}",
                expanded=page.page_number == result.pages[0].page_number
            ):
                display_single_page(page)


def display_single_page(page):
    """Display a single page's content."""
    if page.success:
        if page.has_content:
            st.markdown(page.text)

            with st.expander("📊 Sidmetadata"):
                st.write(f"**Bearbetningstid:** {page.processing_time:.1f}s")
                st.write(f"**Antal ord:** {page.word_count}")
                st.write(f"**Antal tecken:** {len(page.text)}")
        else:
            st.info("Sidan verkar vara tom eller innehåller väldigt lite text.")
    else:
        st.error(f"OCR misslyckades: {page.error}")


# =============================================================================
# MAIN PAGE
# =============================================================================

st.title("📄 OCR")
st.markdown("*Extrahera text från PDF-dokument*")

# Provider Selector (Sidebar)
with st.sidebar:
    st.header("⚙️ OCR-inställningar")

    provider = st.radio(
        UI_TEXT["select_provider"],
        [PROVIDER_GEMINI, PROVIDER_REPLICATE],
        index=0 if DEFAULT_PROVIDER == PROVIDER_GEMINI else 1,
        help="Välj vilken AI-modell som ska användas för OCR."
    )

    token_missing = False
    if provider == PROVIDER_REPLICATE and not REPLICATE_API_TOKEN:
        token_missing = True
        st.error("❌ REPLICATE_API_TOKEN saknas")
    elif provider == PROVIDER_GEMINI and not GOOGLE_API_KEY:
        token_missing = True
        st.error("❌ GOOGLE_API_KEY saknas")

    if token_missing:
        st.info("Lägg till API-nyckeln i `.env`-filen.")

    st.divider()

    # Load saved OCR results
    st.subheader("📂 Ladda sparad OCR")

    # Option 1: Load from saved files
    saved_files = get_saved_ocr_files()
    if saved_files:
        selected_file = st.selectbox(
            "Välj sparad fil",
            options=[""] + [f.name for f in saved_files],
            format_func=lambda x: "-- Välj fil --" if x == "" else x,
            key="saved_file_select"
        )
        if selected_file and st.button("📥 Ladda vald fil", use_container_width=True):
            try:
                file_path = OUTPUT_DIR / selected_file
                st.session_state.ocr_result = load_ocr_result(file_path)
                st.success(f"Laddade: {selected_file}")
                st.rerun()
            except Exception as e:
                st.error(f"Kunde inte ladda: {e}")
    else:
        st.info("Inga sparade filer hittades")

    # Option 2: Upload JSON file
    uploaded_json = st.file_uploader(
        "Eller ladda upp JSON",
        type=["json"],
        key="json_uploader",
        help="Ladda upp en tidigare exporterad OCR JSON-fil"
    )
    if uploaded_json:
        if st.button("📥 Ladda uppladdad JSON", use_container_width=True):
            try:
                st.session_state.ocr_result = load_ocr_from_uploaded_json(uploaded_json)
                st.success(f"Laddade: {uploaded_json.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Kunde inte ladda: {e}")

    st.divider()

    if st.session_state.ocr_result or st.session_state.pdf_bytes:
        if st.button("🗑️ Rensa allt"):
            reset_session_for_new_upload()
            st.session_state.last_uploaded_file = None
            st.rerun()

st.divider()

if token_missing:
    st.warning("⚠️ Konfigurera API-nycklar i menyn till vänster för att fortsätta.")
else:
    uploaded_file = st.file_uploader(
        UI_TEXT["upload_label"],
        type=["pdf"],
        help=UI_TEXT["upload_help"],
    )

    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"Filen är för stor ({file_size_mb:.1f} MB). Max {MAX_FILE_SIZE_MB} MB.")
        else:
            st.success(f"📄 **{uploaded_file.name}** ({file_size_mb:.1f} MB)")

            selected_pages = page_selection_ui(uploaded_file)

            if selected_pages:
                st.divider()

                col1, col2 = st.columns([1, 4])
                with col1:
                    process_button = st.button(
                        f"🚀 {UI_TEXT['start_ocr_btn']} ({len(selected_pages)} sidor)",
                        type="primary",
                        use_container_width=True
                    )

                if process_button:
                    process_document_selected(uploaded_file, provider, selected_pages)

    if st.session_state.ocr_result is not None:
        display_results(st.session_state.ocr_result)

        st.divider()
        st.info("💡 **Nästa steg:** Gå till **Extraktion** i menyn för att extrahera strukturerad information.")
