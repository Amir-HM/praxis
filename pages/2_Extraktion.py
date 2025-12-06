"""
Rättskoll - Extraction Page
============================
Extract structured entities from OCR results using Claude.
"""

import json
import streamlit as st

from config import OPENROUTER_API_KEY
from claude_extractor import ClaudeExtractor, ExtractionError, format_extraction_summary


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Extraktion - Rättskoll",
    page_icon="🔍",
    layout="wide",
)


# =============================================================================
# SESSION STATE
# =============================================================================

if "extraction_result" not in st.session_state:
    st.session_state.extraction_result = None


# =============================================================================
# MAIN PAGE
# =============================================================================

st.title("🔍 Extraktion")
st.markdown("*Extrahera strukturerad information från OCR-resultat*")

# Check for API key
if not OPENROUTER_API_KEY:
    st.error("❌ OPENROUTER_API_KEY saknas")
    st.info("""
    **Så här löser du detta:**
    1. Skapa ett konto på [openrouter.ai](https://openrouter.ai/)
    2. Skapa en API-nyckel på [openrouter.ai/keys](https://openrouter.ai/keys)
    3. Lägg till `OPENROUTER_API_KEY=din_nyckel` i `.env`-filen
    4. Starta om appen
    """)
    st.stop()

st.divider()

# Check for OCR results
if "ocr_result" not in st.session_state or st.session_state.ocr_result is None:
    st.warning("⚠️ Inga OCR-resultat tillgängliga")
    st.info("""
    **Gör så här:**
    1. Gå till **OCR** i menyn till vänster
    2. Ladda upp en PDF
    3. Kör OCR på dokumentet
    4. Kom tillbaka hit för att extrahera information
    """)
    st.stop()

# Display OCR result info
ocr_result = st.session_state.ocr_result
st.success(f"📄 **{ocr_result.filename}** - {ocr_result.total_pages} sidor, {ocr_result.total_words:,} ord")

# Extraction options
st.subheader("Extraheringsinställningar")

col1, col2 = st.columns(2)

with col1:
    extract_timeline = st.checkbox("Tidslinje (händelser med datum/tid)", value=True)
    extract_persons = st.checkbox("Personer (namn och roller)", value=True)

with col2:
    extract_claims = st.checkbox("Påståenden (faktapåståenden)", value=True)

st.divider()

# Extract button
col1, col2 = st.columns([1, 4])
with col1:
    extract_button = st.button(
        "🚀 Starta extraktion",
        type="primary",
        use_container_width=True
    )

if extract_button:
    if not any([extract_timeline, extract_persons, extract_claims]):
        st.error("Välj minst en typ av information att extrahera.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            extractor = ClaudeExtractor()

            def update_progress(current, total, status):
                progress_bar.progress(current / total)
                status_text.text(status)

            result = extractor.extract_from_ocr_result(
                ocr_result,
                progress_callback=update_progress
            )

            st.session_state.extraction_result = result

            progress_bar.progress(100)
            status_text.text("✅ Extraktion klar!")

            st.rerun()

        except ExtractionError as e:
            st.error(f"❌ Extraheringsfel: {e}")
            progress_bar.empty()
            status_text.empty()

        except Exception as e:
            st.error(f"❌ Oväntat fel: {e}")
            progress_bar.empty()
            status_text.empty()

# Display results
if st.session_state.extraction_result is not None:
    result = st.session_state.extraction_result

    st.divider()
    st.subheader("📊 Extraktionsresultat")

    # Statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Tidshändelser", len(result.get("timeline_events", [])))

    with col2:
        st.metric("Personer", len(result.get("persons", [])))

    with col3:
        st.metric("Påståenden", len(result.get("claims", [])))

    with col4:
        st.metric("Sidor bearbetade", result.get("total_pages_processed", 0))

    # Download buttons
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 Ladda ner JSON",
            data=json_data,
            file_name=f"{result.get('source_file', 'extraction').replace('.pdf', '')}_extraction.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        md_data = format_extraction_summary(result)
        st.download_button(
            label="📥 Ladda ner Markdown",
            data=md_data,
            file_name=f"{result.get('source_file', 'extraction').replace('.pdf', '')}_extraction.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # Tabbed view
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Sammanfattning", "📅 Tidslinje", "👥 Personer", "💬 Påståenden"])

    with tab1:
        st.markdown(format_extraction_summary(result))

    with tab2:
        events = result.get("timeline_events", [])
        if events:
            for event in events:
                with st.expander(f"📅 {event.get('datetime_str', 'Okänt datum')} - {event.get('description', '')[:50]}..."):
                    st.write(f"**Beskrivning:** {event.get('description', '')}")
                    st.write(f"**Plats:** {event.get('location', 'Ej angiven')}")
                    st.write(f"**Personer:** {', '.join(event.get('involves_persons', []))}")
                    st.write(f"**Källa:** Sida {event.get('source_page', '?')}")
                    st.info(f"> {event.get('source_quote', '')}")
        else:
            st.info("Inga tidshändelser hittades.")

    with tab3:
        persons = result.get("persons", [])
        if persons:
            # Create a table
            st.markdown("| Namn | Roll | Omnämnd på sidor |")
            st.markdown("|------|------|------------------|")
            for person in persons:
                pages = ", ".join(str(p) for p in person.get("mentioned_pages", []))
                st.markdown(f"| {person.get('name', '')} | {person.get('role', '')} | {pages} |")
        else:
            st.info("Inga personer identifierades.")

    with tab4:
        claims = result.get("claims", [])
        if claims:
            for claim in claims:
                with st.expander(f"💬 {claim.get('claimant', 'Okänd')} (sida {claim.get('source_page', '?')})"):
                    st.write(f"**Påstående:** {claim.get('claim_text', '')}")
                    st.info(f"> {claim.get('source_quote', '')}")
        else:
            st.info("Inga påståenden extraherades.")

# Sidebar
with st.sidebar:
    st.header("ℹ️ Om Extraktion")
    st.markdown("""
    **Extraktion** använder Claude AI för att identifiera:

    - **Tidslinje**: Händelser med datum, tid och plats
    - **Personer**: Namn och roller (misstänkt, vittne, etc.)
    - **Påståenden**: Faktapåståenden med källhänvisning

    Alla extraherade uppgifter inkluderar sidnummer för verifiering.
    """)

    st.divider()

    if st.session_state.extraction_result:
        if st.button("🗑️ Rensa extraktion"):
            st.session_state.extraction_result = None
            st.rerun()
