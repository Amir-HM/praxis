"""
Rättskoll - Claude Entity Extractor
====================================
Extracts structured entities from OCR text using Claude via OpenRouter.
"""

import json
from typing import Optional

import openai

from config import (
    OPENROUTER_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_EXTRACTION_PROMPT,
    CLAUDE_EXTRACTION_CONFIG,
)
from models import OCRResult, TimelineEvent, Person, Claim


class ExtractionError(Exception):
    """Custom exception for extraction errors."""
    pass


class ClaudeExtractor:
    """
    Extracts structured entities from OCR results using Claude via OpenRouter.
    """

    def __init__(self):
        """Initialize OpenRouter client."""
        if not OPENROUTER_API_KEY:
            raise ExtractionError(
                "OPENROUTER_API_KEY saknas. Lägg till i .env-filen."
            )
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        self.model = CLAUDE_MODEL

    def extract_from_page(
        self,
        page_text: str,
        page_number: int
    ) -> dict:
        """
        Extract entities from a single page.

        Args:
            page_text: OCR text from the page
            page_number: Source page number for citations

        Returns:
            Dict with extracted entities
        """
        if not page_text.strip():
            return {
                "timeline_events": [],
                "persons": [],
                "claims": [],
            }

        prompt = f"""{CLAUDE_EXTRACTION_PROMPT}

Sidnummer: {page_number}

Text att analysera:
---
{page_text}
---

Returnera JSON med denna struktur:
{{
    "timeline_events": [
        {{
            "id": "te_1",
            "description": "Beskrivning av händelsen",
            "datetime_str": "2025-01-15 14:30" eller "januari 2025" om osäkert,
            "location": "Plats om angiven",
            "source_page": {page_number},
            "source_quote": "Exakt citat från texten",
            "involves_persons": ["Person A", "Person B"]
        }}
    ],
    "persons": [
        {{
            "id": "p_1",
            "name": "Förnamn Efternamn",
            "role": "misstänkt|vittne|målsägande|polis|annat",
            "mentioned_pages": [{page_number}]
        }}
    ],
    "claims": [
        {{
            "id": "c_1",
            "claim_text": "Påståendet som görs",
            "claimant": "Vem som gör påståendet",
            "source_page": {page_number},
            "source_quote": "Exakt citat"
        }}
    ]
}}

Om ingen relevant information finns, returnera tomma listor."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=CLAUDE_EXTRACTION_CONFIG["max_tokens"],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse the response
            content = response.choices[0].message.content

            # Try to extract JSON from response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                return {
                    "timeline_events": [],
                    "persons": [],
                    "claims": [],
                }

            json_str = content[json_start:json_end]
            result = json.loads(json_str)

            return result

        except json.JSONDecodeError as e:
            raise ExtractionError(f"Kunde inte tolka JSON från Claude: {e}")
        except Exception as e:
            raise ExtractionError(f"Extraction misslyckades: {e}")

    def extract_from_ocr_result(
        self,
        ocr_result: OCRResult,
        progress_callback: Optional[callable] = None
    ) -> dict:
        """
        Extract entities from complete OCR result.

        Args:
            ocr_result: OCRResult with all pages
            progress_callback: Optional callback(current, total, status)

        Returns:
            Dict with all extracted entities, merged across pages
        """
        all_timeline_events = []
        all_persons = {}  # Use dict to merge by name
        all_claims = []

        total_pages = len(ocr_result.pages)

        for i, page in enumerate(ocr_result.pages):
            if progress_callback:
                progress_callback(
                    i + 1,
                    total_pages,
                    f"Extraherar från sida {page.page_number}..."
                )

            if not page.success or not page.has_content:
                continue

            try:
                page_result = self.extract_from_page(
                    page.text,
                    page.page_number
                )

                # Add timeline events
                for event in page_result.get("timeline_events", []):
                    event["id"] = f"te_{len(all_timeline_events) + 1}"
                    all_timeline_events.append(event)

                # Merge persons by name
                for person in page_result.get("persons", []):
                    name = person.get("name", "").strip()
                    if name:
                        if name in all_persons:
                            # Add page to existing person
                            existing_pages = all_persons[name].get("mentioned_pages", [])
                            new_pages = person.get("mentioned_pages", [])
                            all_persons[name]["mentioned_pages"] = list(
                                set(existing_pages + new_pages)
                            )
                        else:
                            person["id"] = f"p_{len(all_persons) + 1}"
                            all_persons[name] = person

                # Add claims
                for claim in page_result.get("claims", []):
                    claim["id"] = f"c_{len(all_claims) + 1}"
                    all_claims.append(claim)

            except ExtractionError:
                # Skip failed pages but continue
                continue

        return {
            "timeline_events": all_timeline_events,
            "persons": list(all_persons.values()),
            "claims": all_claims,
            "source_file": ocr_result.filename,
            "total_pages_processed": total_pages,
        }


def format_extraction_summary(extraction_result: dict) -> str:
    """
    Format extraction result as readable summary.

    Args:
        extraction_result: Dict from extract_from_ocr_result

    Returns:
        Formatted string summary
    """
    lines = [
        f"# Extraktion från {extraction_result.get('source_file', 'dokument')}",
        f"",
        f"**Sidor bearbetade:** {extraction_result.get('total_pages_processed', 0)}",
        f"",
    ]

    # Timeline events
    events = extraction_result.get("timeline_events", [])
    lines.append(f"## Tidslinje ({len(events)} händelser)")
    lines.append("")
    if events:
        for event in events:
            lines.append(f"### {event.get('datetime_str', 'Okänt datum')}")
            lines.append(f"**Plats:** {event.get('location', 'Ej angiven')}")
            lines.append(f"**Beskrivning:** {event.get('description', '')}")
            lines.append(f"**Personer:** {', '.join(event.get('involves_persons', []))}")
            lines.append(f"**Källa:** Sida {event.get('source_page', '?')}")
            lines.append(f"> {event.get('source_quote', '')}")
            lines.append("")
    else:
        lines.append("*Inga tidshändelser hittades*")
        lines.append("")

    # Persons
    persons = extraction_result.get("persons", [])
    lines.append(f"## Personer ({len(persons)} identifierade)")
    lines.append("")
    if persons:
        lines.append("| Namn | Roll | Sidor |")
        lines.append("|------|------|-------|")
        for person in persons:
            pages = ", ".join(str(p) for p in person.get("mentioned_pages", []))
            lines.append(f"| {person.get('name', '')} | {person.get('role', '')} | {pages} |")
        lines.append("")
    else:
        lines.append("*Inga personer identifierades*")
        lines.append("")

    # Claims
    claims = extraction_result.get("claims", [])
    lines.append(f"## Påståenden ({len(claims)} extraherade)")
    lines.append("")
    if claims:
        for claim in claims:
            lines.append(f"- **{claim.get('claimant', 'Okänd')}** (sida {claim.get('source_page', '?')}):")
            lines.append(f"  {claim.get('claim_text', '')}")
            lines.append("")
    else:
        lines.append("*Inga påståenden extraherades*")
        lines.append("")

    return "\n".join(lines)
