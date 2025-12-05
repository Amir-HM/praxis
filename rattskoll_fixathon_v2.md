# RÄTTSKOLL

**Norrsken Fixathon 2025 | Society Track**

**Talk to the law. Audit the case.**

---

## The Story

My mother was convicted. We believe she is innocent. We hired lawyers. We appealed. It took six months to get one forensic expert to review the evidence. The appeal was denied.

I spent weeks trying to understand a thousand-page preliminary investigation protocol (FUP). The language was impenetrable. The structure was chaos. Key details were buried. Contradictions went unnoticed.

We weren't looking for legal advice. We just needed to *understand*.

The law isn't hidden because it's complex. It's hidden because no one has built a bridge.

---

## The Problem

A Swedish FUP can be 1,000+ pages of scanned documents — witness statements, police reports, forensic evidence, interrogations — all unstructured and written in bureaucratic Swedish.

No normal person can audit this. Even lawyers struggle to cross-reference every detail. That's how errors slip through: wrong timestamps, impossible travel times, contradictory witnesses. These errors lead to wrongful convictions.

Meanwhile, Swedish law is public. Court rulings are online. But citizens can't access what they can't understand.

**Result:** Those who can afford expert lawyers navigate. Everyone else guesses. Trust in institutions erodes.

---

## The Solution

**Rättskoll** bridges the gap between citizens and the Swedish legal system.

Two modes:

| Mode | What It Does | Who It's For |
|------|--------------|--------------|
| **Talk to the Law** | Conversational AI for legal orientation | Any citizen with a legal question |
| **FUP Forensic Audit** | AI-powered case analysis and inconsistency detection | Defendants, families, defense teams |

---

## Mode 1: FUP Forensic Audit

**Upload a case file. Get a structured analysis. Spot what humans miss.**

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
│  AI agents cross-check for:                              │
│                                                          │
│  ⏱️  TIMELINE CONFLICTS                                  │
│      "Witness says 14:00, phone records show 14:15"      │
│                                                          │
│  👥 WITNESS CONTRADICTIONS                               │
│      "Blue car on p.45, black car on p.203"              │
│                                                          │
│  🚗 PHYSICAL IMPOSSIBILITIES                             │
│      "Claimed 20 min travel, minimum is 45 min"          │
│                                                          │
│  📁 EVIDENCE GAPS                                        │
│      "DNA mentioned p.12, no lab report in file"         │
│                                                          │
│  ✓  USER CLAIM VERIFICATION                              │
│      User inputs their version → AI checks against FUP   │
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
│     Interactive, all events mapped, conflicts marked     │
│                                                          │
│  ⚠️  INCONSISTENCIES                                     │
│     Ranked by severity, with page citations              │
│                                                          │
│  ❓ ACTION ITEMS                                         │
│     "Request cell tower logs for [date]"                 │
│     "Clarify travel time discrepancy"                    │
│     "Ask why report X is missing from file"              │
│                                                          │
│  📑 SEARCHABLE INDEX                                     │
│     Full document structure, linked to pages             │
│                                                          │
│  Output: PDF report + interactive web view               │
└──────────────────────────────────────────────────────────┘
```

### Why This Matters

- **No lawyer has time** to manually cross-reference 1,000 pages
- **Families become informed partners**, not passive observers
- **Catches errors** that lead to wrongful convictions
- **Supports appeals** by systematically identifying missed grounds
- **Every finding is cited** — page numbers, no hallucinations

---

## Mode 2: Talk to the Law

**Describe your situation. Get relevant law and precedent.**

For citizens who don't have a case file — they just have a question.

### Features

1. **Legal Chat** — Describe situation in plain Swedish
2. **Law Search** — RAG over indexed Swedish law (SFS via lagen.nu)
3. **Precedent Finder** — Matches to similar Supreme Court rulings
4. **Plain Language** — Explains legal text in everyday Swedish
5. **Next Steps** — Actionable guidance, including when to get a lawyer

### Use Cases

| Persona | Question |
|---------|----------|
| Tenant | "My landlord wants to evict me. What are my rights?" |
| Employee | "I was fired without warning. Is this legal?" |
| Immigrant | "My residence permit was denied. Can I appeal?" |
| Family | "What are the grounds for appeal in a criminal case?" |

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
- [ ] Timeline conflict detection
- [ ] Witness contradiction checker
- [ ] Evidence gap identifier
- [ ] User claim verification input

### Hours 16-20: Report & Polish
- [ ] Report generation (summary, findings, actions)
- [ ] Visual timeline component
- [ ] Export to PDF

### Hours 20-24: Demo Prep
- [ ] Test with sample FUP
- [ ] Fix critical bugs
- [ ] Prepare demo script
- [ ] Record backup video

### Stretch Goals (if time)
- [ ] Google Maps API for travel time validation
- [ ] Weather API for condition verification
- [ ] Law/praxis linking in report

---

## The Team

Two technical founders. AI, low-code, design.

We've built products. But this one is personal.

We're building Rättskoll because we needed it and it didn't exist.

---

## Why Society Track

The Fixathon brief:

> *"Trust in institutions is strained, making transparency and citizen engagement vital. The challenge is to use AI not just for efficiency, but to strengthen trust, equity, and sustainability in the public sector."*

Rättskoll is transparency infrastructure.

When citizens can audit the case against them — when they can see the law in language they understand — trust is restored. Not because outcomes change, but because the process becomes legible.

Justice shouldn't require a law degree. It should require access.

---

## Vision

**Sweden first.** Open-source from day one.

Every civil law country — Germany, France, Netherlands, Brazil — has codified law and published precedent. The architecture we build for Sweden scales globally.

---

## The Ask

24 hours. Two builders. One bridge.

**Rättskoll: Talk to the law. Audit the case.**
