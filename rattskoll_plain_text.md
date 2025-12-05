# RÄTTSKOLL

Norrsken Fixathon 2025 | Society Track

Talk to the law. Audit the case.


## The Story

My mother was convicted. We believe she is innocent. We hired lawyers. We appealed. It took six months to get one forensic expert to review the evidence. The appeal was denied.

I spent weeks trying to understand a thousand-page preliminary investigation protocol (FUP). The language was impenetrable. The structure was chaos. Key details were buried. Potential contradictions went unnoticed.

We weren't looking for legal advice. We just needed to understand.

The law isn't hidden because it's complex. It's hidden because no one has built a bridge.


## The Problem

A Swedish FUP can be 1,000+ pages of scanned documents — witness statements, police reports, forensic evidence, interrogations — often unstructured and written in bureaucratic Swedish.

Manual cross-referencing of this volume is time-intensive and error-prone. Details can be missed: timestamp discrepancies, inconsistent witness accounts, gaps in evidence chains. Such oversights can contribute to unjust outcomes.

Meanwhile, Swedish law is public and court rulings are online, but many citizens struggle to access what they can't understand.

Those with resources to engage expert help can navigate the system effectively. Others may struggle. This asymmetry can undermine public trust in justice institutions.


## The Solution

Rättskoll aims to bridge the gap between citizens and the Swedish legal system through two modes:

MODE 1: FUP FORENSIC AUDIT
AI-assisted case analysis and inconsistency detection for defendants, families, and defense teams.

MODE 2: TALK TO THE LAW  
Conversational AI for legal orientation, for any citizen with a legal question.


## FUP Forensic Audit — How It Works

Upload a case file. Get a structured analysis. Surface what might otherwise be missed.

STAGE 1: OCR + EXTRACTION
State-of-the-art OCR (such as GOT-OCR 2.0 or Surya) processes scanned PDFs, handling handwriting, stamps, and complex layouts. Page numbers are preserved for citations.

STAGE 2: DOCUMENT STRUCTURING
AI identifies and labels document types: witness statements, police reports, interrogations, forensic evidence, expert opinions, evidence inventories. Output is a structured index with page references.

STAGE 3: ENTITY & CLAIM EXTRACTION
The system extracts and indexes: people (names, roles, relationships), places (addresses, locations), times (dates, timestamps, durations), claims (what each source asserts), and evidence items. Everything links back to source pages.

STAGE 4: CONSISTENCY ANALYSIS
AI agents review the structured data and flag potential issues:
- Timeline discrepancies (e.g., witness says 14:00, phone records show 14:15)
- Witness inconsistencies (e.g., different descriptions across statements)
- Logistical questions (e.g., claimed travel times worth verifying)
- Potential evidence gaps (e.g., referenced items not found in file)
- User claim comparison (user inputs their account, AI compares to FUP)

STAGE 5: REPORT GENERATION
The system produces a report containing: case summary (key allegations, main evidence, critical dates), visual timeline (all events mapped, potential conflicts marked), flagged items (potential inconsistencies with page citations), suggested follow-ups (questions to investigate, documents to request), and a searchable index of the full document structure.

Output is available as PDF report and interactive web view.


## Talk to the Law — How It Works

For citizens without a case file who simply have a legal question.

The user describes their situation in plain Swedish. The system searches indexed Swedish law (SFS via lagen.nu) and court precedent, then responds with relevant legal provisions, similar court rulings, plain-language explanations, and suggested next steps — including when to consult a lawyer.

Example use cases: tenants facing eviction, employees with termination questions, immigrants appealing permit decisions, families exploring appeal options.


## Technical Approach

Frontend: Lovable for rapid prototyping
OCR: GOT-OCR 2.0, Surya, or Azure Document Intelligence
LLM: Claude API or GPT-4
Vector Database: Supabase pgvector or Pinecone
Law Data: lagen.nu (open source), domstol.se (court rulings)
Hosting: Vercel


## 24-Hour Build Plan

Hours 0-4: Set up project, basic UI, PDF upload, OCR pipeline
Hours 4-10: Document structuring, entity extraction, timeline generation, page reference system
Hours 10-16: Discrepancy detection, inconsistency flagging, evidence gap identification, user claim comparison
Hours 16-20: Report generation, visual timeline, PDF export
Hours 20-24: Testing, bug fixes, demo preparation

Stretch goals: Maps API for travel time context, weather API for condition verification, law/praxis linking in reports.


## The Team

Two technical founders with experience in AI, low-code tools, and design.

We've built products before. But this one is personal. We're building Rättskoll because we needed it and it didn't exist.


## Why Society Track

The Fixathon brief states: "Trust in institutions is strained, making transparency and citizen engagement vital. The challenge is to use AI not just for efficiency, but to strengthen trust, equity, and sustainability in the public sector."

Rättskoll aims to be transparency infrastructure. When citizens can better understand the case against them — when they can see the law in language they understand — it may help restore trust. Not because outcomes necessarily change, but because the process becomes more legible.

Access to understanding shouldn't require a law degree.


## Vision

Sweden first. Open-source from day one.

Many civil law countries have codified law and published precedent. The architecture we build for Sweden could potentially be adapted for other jurisdictions.


## The Ask

24 hours. Two builders. One bridge.

Rättskoll: Talk to the law. Audit the case.
