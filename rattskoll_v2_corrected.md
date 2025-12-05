# RÄTTSKOLL

**Norrsken Fixathon 2025 | Society Track**

**Talk to the law. Audit the case.**

---

## The Story

My mother was convicted. We believe she is innocent. We hired lawyers. We appealed. It took six months to get one forensic expert to review the evidence. The appeal was denied.

I spent weeks trying to understand a thousand-page preliminary investigation protocol (FUP). The language was impenetrable. The structure was chaos. Key details were buried. Potential contradictions went unnoticed.

We weren't looking for legal advice. We just needed to *understand*.

The law isn't hidden because it's complex. It's hidden because no one has built a bridge.

---

## The Problem

A Swedish FUP can be 1,000+ pages of scanned documents — witness statements, police reports, forensic evidence, interrogations — often unstructured and written in bureaucratic Swedish.

Manual cross-referencing of this volume is time-intensive and error-prone. Details can be missed: timestamp discrepancies, inconsistent witness accounts, gaps in evidence chains. Such oversights can contribute to unjust outcomes.

Meanwhile, Swedish law is public. Court rulings are online. But many citizens struggle to access what they can't understand.

**Result:** Those with resources to engage expert help can navigate the system effectively. Others may struggle. This asymmetry can undermine public trust in justice institutions.

---

## The Solution

**Rättskoll** aims to bridge the gap between citizens and the Swedish legal system.

Two modes:

| Mode | What It Does | Who It's For |
|------|--------------|--------------|
| **Talk to the Law** | Conversational AI for legal orientation | Any citizen with a legal question |
| **FUP Forensic Audit** | AI-assisted case analysis and inconsistency detection | Defendants, families, defense teams |

---

## Mode 1: FUP Forensic Audit

**Upload a case file. Get a structured analysis. Surface what might otherwise be missed.**

### The Pipeline

```
SCANNED FUP (PDF)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 1: OCR + Extraction                               │
│  ────────────────────────────────────────────────────    │
│  • State-of-the-art OCR (GOT-OCR 2.0 / Surya)           │
│  • Handles scans, handwriting, stamps                    │
│  • Preserves page numbers for citations                  │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 2: Document Structuring                           │
│  ────────────────────────────────────────────────────    │
│  AI identifies and labels:                               │
│  • Witness statements (who said what, when)              │
│  • Police reports and interrogations                     │
│  • Forensic evidence (DNA, digital, physical)            │
│  • Expert opinions                                       │
│  • Evidence inventory                                    │
│                                                          │
│  Output: Structured index with page references           │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 3: Entity & Claim Extraction                      │
│  ────────────────────────────────────────────────────    │
│  Extract and index:                                      │
│  • PEOPLE — names, roles, relationships                  │
│  • PLACES — addresses, locations                         │
│  • TIMES — dates, timestamps, durations                  │
│  • CLAIMS — what each source asserts happened            │
│  • EVIDENCE — inventory of physical/digital items        │
│                                                          │
│  Everything linked to source page                        │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 4: Consistency Analysis (Agent Flow)              │
│  ────────────────────────────────────────────────────    │
│  AI agents flag potential issues:                        │
│                                                          │
│  ⏱️  TIMELINE DISCREPANCIES                              │
│      "Witness says 14:00, phone records show 14:15"      │
│                                                          │
│  👥 WITNESS INCONSISTENCIES                              │
│      "Blue car on p.45, black car on p.203"              │
│                                                          │
│  🚗 LOGISTICAL QUESTIONS                                 │
│      "Claimed 20 min travel — worth verifying"           │
│                                                          │
│  📁 POTENTIAL EVIDENCE GAPS                              │
│      "DNA mentioned p.12, no lab report found in file"   │
│                                                          │
│  ✓  USER CLAIM COMPARISON                                │
│      User inputs their account → AI compares to FUP      │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 5: Report Generation                              │
│  ────────────────────────────────────────────────────    │
│                                                          │
│  📋 CASE SUMMARY                                         │
│     Key allegations, main evidence, critical dates       │
│                                                          │
│  🕐 VISUAL TIMELINE                                      │
│     All events mapped, potential conflicts marked        │
│                                                          │
│  ⚠️  FLAGGED ITEMS                                       │
│     Potential inconsistencies, with page citations       │
│                                                          │
│  ❓ SUGGESTED FOLLOW-UPS                                 │
│     "Consider requesting cell tower logs for [date]"     │
│     "May be worth clarifying travel time"                │
│     "Note: report X appears to be missing from file"     │
│                                                          │
│  📑 SEARCHABLE INDEX                                     │
│     Full document structure, linked to pages             │
│                                                          │
│  Output: PDF report + interactive web view               │
└──────────────────────────────────────────────────────────┘
```

### Why This Matters

- **Reduces manual review burden** for lengthy case files
- **Helps families become informed participants** in the process
- **Surfaces potential inconsistencies** that merit further investigation
- **Supports appeals** by systematically organizing case material
- **Every finding is cited** — page numbers provided, sources traceable

---

## Mode 2: Talk to the Law

**Describe your situation. Get relevant law and precedent.**

For citizens who don't have a case file — they just have a question.

### Features

1. **Legal Chat** — Describe situation in plain Swedish
2. **Law Search** — RAG over indexed Swedish law (SFS via lagen.nu)
3. **Precedent Finder** — Matches to similar court rulings
4. **Plain Language** — Explains legal text in everyday Swedish
5. **Next Steps** — Suggested actions, including when to consult a lawyer

### Example Use Cases

| Persona | Question |
|---------|----------|
| Tenant | "My landlord wants to evict me. What does the law say?" |
| Employee | "I was fired without warning. What are my rights?" |
| Immigrant | "My residence permit was denied. What are my options?" |
| Family | "What are possible grounds for appeal in a criminal case?" |

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       RÄTTSKOLL                             │
└─────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         ▼                                     ▼
┌─────────────────────┐             ┌─────────────────────┐
│   FUP FORENSIC      │             │   TALK TO THE LAW   │
│   AUDIT             │             │                     │
│                     │             │                     │
│ • PDF Upload        │             │ • Chat Interface    │
│ • OCR Pipeline      │             │ • Question Router   │
│ • Structuring AI    │             │                     │
│ • Agent Analysis    │             │                     │
│ • Report Gen        │             │                     │
└─────────────────────┘             └─────────────────────┘
         │                                     │
         └──────────────────┬──────────────────┘
                            ▼
              ┌───────────────────────┐
              │     SHARED LAYER      │
              │                       │
              │ • Law Index (lagen.nu)│
              │ • Praxis Index (HD)   │
              │ • Vector DB           │
              │ • LLM (Claude/GPT-4)  │
              └───────────────────────┘
```

### Tech Stack

| Component | Tool |
|-----------|------|
| Frontend | Lovable (rapid prototyping) |
| OCR | GOT-OCR 2.0 / Surya / Azure Doc Intelligence |
| LLM | Claude API or GPT-4 |
| Vector DB | Supabase pgvector or Pinecone |
| Law Data | lagen.nu (open), domstol.se (rulings) |
| Hosting | Vercel |

---

## 24-Hour Build Plan

### Hours 0-4: Foundation
- [ ] Set up Lovable project
- [ ] Basic chat UI
- [ ] PDF upload component
- [ ] OCR pipeline (GOT-OCR or Surya)

### Hours 4-10: Core FUP Audit
- [ ] Document structuring prompts
- [ ] Entity extraction (people, places, times, claims)
- [ ] Basic timeline generation
- [ ] Page reference system

### Hours 10-16: Analysis Engine
- [ ] Timeline discrepancy detection
- [ ] Witness inconsistency flagger
- [ ] Evidence gap identifier
- [ ] User claim comparison input

### Hours 16-20: Report & Polish
- [ ] Report generation (summary, findings, suggestions)
- [ ] Visual timeline component
- [ ] Export to PDF

### Hours 20-24: Demo Prep
- [ ] Test with sample documents
- [ ] Fix critical bugs
- [ ] Prepare demo script
- [ ] Record backup video

### Stretch Goals (if time)
- [ ] Maps API for travel time context
- [ ] Weather API for condition context
- [ ] Law/praxis linking in report

---

## The Team

Two technical founders with experience in AI, low-code tools, and design.

We've built products before. But this one is personal.

We're building Rättskoll because we needed it and it didn't exist.

---

## Why Society Track

The Fixathon brief states:

> *"Trust in institutions is strained, making transparency and citizen engagement vital. The challenge is to use AI not just for efficiency, but to strengthen trust, equity, and sustainability in the public sector."*

Rättskoll aims to be transparency infrastructure.

When citizens can better understand the case against them — when they can see the law in language they understand — it may help restore trust. Not because outcomes necessarily change, but because the process becomes more legible.

Access to understanding shouldn't require a law degree.

---

## Vision

**Sweden first.** Open-source from day one.

Many civil law countries — Germany, France, Netherlands, Brazil — have codified law and published precedent. The architecture we build for Sweden could potentially be adapted for other jurisdictions.

---

## The Ask

24 hours. Two builders. One bridge.

**Rättskoll: Talk to the law. Audit the case.**
