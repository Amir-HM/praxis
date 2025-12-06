"""
Rättskoll - AI Forensic Auditor
================================
Main entry point for the Rättskoll multi-page application.
"""

import streamlit as st

from config import (
    PAGE_TITLE,
    PAGE_ICON,
    REPLICATE_API_TOKEN,
    GOOGLE_API_KEY,
    OPENROUTER_API_KEY,
)


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    .feature-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# MAIN PAGE
# =============================================================================

st.title("🔍 Rättskoll")
st.markdown("### *AI Forensic Auditor för svenska förundersökningsprotokoll*")

st.divider()

# Introduction
st.markdown("""
**Rättskoll** analyserar svenska förundersökningsprotokoll (FUP:ar) för att identifiera
inkonsistenser som kan tyda på felaktiga fällande domar.

Systemet hjälper till att hitta:
- **Tidslinjekonflikter** - samma person på olika platser samtidigt
- **Vittnemotsägelser** - motstridiga uppgifter från olika källor
- **Bevisluckor** - omnämnd bevisning som aldrig testades
- **Fysiska omöjligheter** - resor som är omöjliga på angiven tid
""")

st.divider()

# Feature cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📄 1. OCR</div>
        <p>Ladda upp PDF-dokument och extrahera text med AI-driven OCR.
        Välj specifika sidor att bearbeta och exportera urval som ny PDF.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Gå till OCR →", key="goto_ocr", use_container_width=True):
        st.switch_page("pages/1_OCR.py")

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🔍 2. Extraktion</div>
        <p>Extrahera strukturerad information från OCR-resultat:
        tidshändelser, personer, påståenden - med sidnummer för varje uppgift.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Gå till Extraktion →", key="goto_extraction", use_container_width=True):
        st.switch_page("pages/2_Extraktion.py")

st.divider()

# API Status
st.subheader("🔑 API-status")

col1, col2, col3 = st.columns(3)

with col1:
    if GOOGLE_API_KEY:
        st.success("✅ Google Gemini")
    else:
        st.error("❌ Google Gemini")

with col2:
    if REPLICATE_API_TOKEN:
        st.success("✅ Replicate")
    else:
        st.error("❌ Replicate")

with col3:
    if OPENROUTER_API_KEY:
        st.success("✅ OpenRouter (Claude)")
    else:
        st.error("❌ OpenRouter (Claude)")

if not all([GOOGLE_API_KEY, OPENROUTER_API_KEY]):
    st.info("""
    **Saknade API-nycklar?** Lägg till dem i `.env`-filen:
    ```
    GOOGLE_API_KEY=din_nyckel
    OPENROUTER_API_KEY=din_nyckel
    REPLICATE_API_TOKEN=din_nyckel
    ```
    """)

# Sidebar
with st.sidebar:
    st.header("ℹ️ Om Rättskoll")
    st.markdown("""
    **Rättskoll** är ett AI-system för forensisk analys
    av svenska förundersökningsprotokoll.

    ### Arbetsflöde
    1. **OCR** - Extrahera text från PDF
    2. **Extraktion** - Identifiera entiteter
    3. **Analys** - Hitta inkonsistenser *(kommer)*
    4. **Rapport** - Generera sammanfattning *(kommer)*

    ### Teknologi
    - **OCR:** Gemini / DeepSeek
    - **Extraktion:** Claude
    - **UI:** Streamlit
    """)

    st.divider()
    st.caption("Rättskoll v0.4 - Multi-page App")


# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p><strong>Rättskoll</strong> - Forensisk dokumentanalys för rättssäkerhet</p>
    <p>Alla extraherade uppgifter inkluderar sidnummer för manuell verifiering.</p>
</div>
""", unsafe_allow_html=True)
