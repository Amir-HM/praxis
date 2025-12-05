# RÄTTSKOLL

**Norrsken Fixathon 2025 | Society Track**

---

## Why We're Building This

My mother was convicted. We believe she is innocent. We hired lawyers. We appealed. It took six months to get one forensic expert to review the evidence. The appeal was denied.

I spent weeks trying to understand a thousand-page preliminary investigation protocol. The language was impenetrable. The structure was chaos. We weren't looking for legal advice — we just needed to *understand*.

The law isn't hidden because it's complex. It's hidden because no one has built a bridge.

---

## The Problem

Swedish law is public. Court rulings are online. Yet for most citizens, the justice system is a black box.

MIT researchers found that legal language functions as a signal of authority that excludes ordinary people. Sweden's post-conviction review system is notoriously difficult to navigate without professional help.

Result: those who can afford lawyers navigate. Everyone else guesses. This erodes trust in the institutions democracy depends on.

---

## The Solution

**Rättskoll: Talk to the law.**

A conversational AI that connects citizens to Swedish law and court precedent — not as legal advice, but as legal *orientation*.

---

## What We'll Build (24h MVP)

### Core Features

**1. Legal Chat Interface**
- User describes their situation in plain Swedish
- AI identifies relevant legal domains (criminal, tenancy, employment, immigration, etc.)
- Responds conversationally with context-aware guidance

**2. Law Index Search (RAG)**
- Indexed Swedish law code (SFS) via lagen.nu
- Semantic search — not keyword matching
- Returns relevant paragraphs with plain-language explanations

**3. Precedent Finder**
- Indexed Supreme Court (HD) and Court of Appeal (HovR) rulings
- Matches user situation to similar decided cases
- Summarizes holdings and outcomes

**4. Document Decoder**
- Upload a legal document (rejection letter, FUP excerpt, contract clause)
- AI explains what it says in plain Swedish
- Highlights key dates, obligations, and rights

**5. Action Generator**
- Based on analysis, generates prioritized next steps
- "Questions to ask a lawyer"
- "Documents to request"
- "Deadlines to note"
- "Relevant authorities to contact"

### Technical Architecture

```
User Input (situation / document)
        │
        ▼
┌─────────────────┐
│   AI Router     │ ← Identifies legal domain
└─────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│          RAG Pipeline               │
│  ┌───────────┐    ┌──────────────┐  │
│  │ Law Index │    │ Praxis Index │  │
│  │ (lagen.nu)│    │ (domstol.se) │  │
│  └───────────┘    └──────────────┘  │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────┐
│  LLM Synthesis  │ ← Plain Swedish output
└─────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│            Output                    │
│  • Relevant law (cited)             │
│  • Similar cases (summarized)       │
│  • Plain-language explanation       │
│  • Actionable next steps            │
└─────────────────────────────────────┘
```

### Tech Stack
- **Frontend**: Lovable (rapid UI)
- **AI/LLM**: Claude or GPT-4 via API
- **Vector DB**: Pinecone or Supabase pgvector
- **Data sources**: lagen.nu (law), domstol.se (rulings)
- **Hosting**: Vercel or Netlify

---

## Who It Serves

| Persona | Situation |
|---------|-----------|
| Defendant | Understanding the case against them |
| Family | Exploring appeal options for a loved one |
| Tenant | Facing eviction, unsure of rights |
| Employee | Wrongful termination dispute |
| Immigrant | Residence permit denied |

---

## Why Society Track

The brief states: *"Trust in institutions is strained, making transparency and citizen engagement vital."*

Rättskoll is transparency infrastructure. When citizens can see the law in language they understand, trust is restored — not because outcomes change, but because the process becomes legible.

---

## The Team

Two technical founders. AI, low-code, design. We've built products before.

We're not building this because it's a good idea. We're building it because we needed it and it didn't exist.

---

## Commitment

Open-source from day one. Sweden first, then every civil law country with codified law and published precedent.

---

**Rättskoll: Talk to the law.**
