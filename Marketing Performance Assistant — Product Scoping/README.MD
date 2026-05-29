# Task 1: Product Scoping — Marketing Performance Assistant

## What's in This Folder

| File | What It Is |
|---|---|
| `PRODUCT_BRIEF.md` | The main brief: what the tool is, who it's for, what it does, and what it needs to work |
| `SCOPE.md` | Detailed breakdown of what's in and out of v1, with reasoning for each decision |
| `FLOW_DIAGRAM.md` | ASCII/text diagrams of the user interaction flow and the data pipeline flow |
| `WALKTHROUGH.md` | Written narrative of how I thought through this — the reasoning behind the reasoning |

---

## The Short Version

The tool is called the **Marketing Performance Assistant (MPA)**. It's a lightweight internal web app that answers one question well:

> *"How is our marketing performing across channels right now, and where should we be paying attention?"*

It does this by pulling data from the team's existing marketing platforms (via their APIs), storing it in a central data store, and presenting a structured snapshot with a plain-language summary — refreshed daily, always available, consistent regardless of who opens it.

The primary user is the **internal analyst or account manager**, not the client. That's a deliberate scoping decision explained in the brief.

---

## Decisions I Made and Would Revisit

**I'd revisit:** The plain-language summary approach. I've proposed a rule-based system for v1. That's safe and explainable, but it won't produce summaries that feel genuinely insightful. With more time, I'd prototype a few different approaches and test them with actual users before committing.

**I'd revisit:** The assumption that daily refresh is enough. I've assumed a 7am daily pull is sufficient for the use case. That might be wrong — some teams need same-day data for decisions that happen in the afternoon. Worth validating before building the connector schedule.

**I'd revisit:** Whether BigQuery is the right storage layer for v1. It's the right long-term answer, and it's what the broader org uses, so it makes sense. But at very low data volumes in the earliest stages, even a well-structured Google Sheet would work and would be faster to set up. I'd make a call based on how quickly the team can spin up a BigQuery project.

**I wouldn't revisit:** The decision to make this internal-first. Building a client-facing tool before the internal version is trusted and stable would be a mistake. Do it in the right order.

---

## What I'd Do With More Time

- Spend time with actual users before finalising anything — watch how they currently answer the performance question, not just ask them how they'd want to
- Build a rough clickable wireframe (Figma or even a quick HTML mockup) to test the interaction model
- Map the exact API capabilities and limitations of each platform connector before committing to the data model
- Run a small data test: pull one week of data from one platform manually, transform it, and verify the summary generation logic produces something useful

---

## How to Read This

Start with `PRODUCT_BRIEF.md` — that's the main document and covers the full picture.

Then read `SCOPE.md` if you want the explicit in/out breakdown.

Then read `WALKTHROUGH.md` if you want to understand the reasoning behind the decisions, including what I considered and ruled out.

`FLOW_DIAGRAM.md` is a quick visual reference — useful if you're trying to understand the data architecture at a glance.
