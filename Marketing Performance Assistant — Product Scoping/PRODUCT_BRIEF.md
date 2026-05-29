# Product Brief: Marketing Performance Assistant (MPA)

**Version:** 1.0 Draft  
**Author:** BALAJI V  
**Date:** May 2026  
**Status:** Draft for review
---

## The Problem (In Plain Language)

Right now, when someone asks "how is our marketing performing?", the answer depends entirely on who you ask and when you ask them. One analyst pulls from Google Analytics, another checks the Meta Ads dashboard, someone else exports a CSV from HubSpot, and then someone has to stitch all of that together in a Google Sheet or a slide deck.

The result? The answer is almost always late, often inconsistent, and mentally expensive for whoever has to produce it. If the person who knows where everything lives is on leave, the question just doesn't get answered.

That is the actual problem. Not a lack of data — there's plenty of data. The problem is that producing a coherent picture of marketing performance is a manual, person-dependent process that shouldn't have to be.

---

## What I'm Proposing

A lightweight internal tool I'm calling the **Marketing Performance Assistant** — or MPA for short.

The core idea is simple: a single place where someone can ask "how are we doing across channels?" and get a structured, consistent answer without digging through five different platforms.

This is not a grand BI dashboard. It's not a replacement for Google Analytics or Meta Ads. It's a thin layer that sits on top of the tools the team already uses and answers one question well:

> **"What's the current performance picture, and where should we be paying attention?"**

---

## Who This Is For

I went back and forth on this, but I landed on the **internal analyst or account manager** as the primary user — not the client.

Here's my reasoning: clients want polished, contextual answers. They want explanations, not raw numbers. Building a tool that's client-facing means you need to think about data trust, branding, access control, and how numbers are explained when they're bad. That's a much harder problem.

Internal team members, on the other hand, just need the answer fast. They can handle a rougher interface. They know what the numbers mean. And if the tool makes *their* lives easier, they'll also be better equipped to answer client questions quickly and confidently.

So: **primary user = internal analyst/account manager**. Client-facing output is out of scope for v1.

---

## What the Tool Does in V1

The v1 tool does three things and only three things:

### 1. Pulls a performance snapshot
When a team member opens the tool and selects a client brand, they see a summary of that brand's key marketing metrics across active channels — things like impressions, clicks, spend, conversions, and cost-per-result — for a default time window (last 7 days, with an option to switch to last 30).

This is not a live feed. It's a snapshot that refreshes on a schedule (more on that below). The goal is "accurate enough and always available," not "real-time."

### 2. Flags what's changed
Raw numbers are useful. Changes are more useful. The tool highlights metrics that have moved meaningfully — up or down — compared to the previous period. A user shouldn't need to remember last week's numbers to know if something is off.

This is a simple percentage delta calculation. Nothing fancy. But it means someone opening the tool at 9am Monday gets the important stuff surfaced, not buried.

### 3. Surfaces a plain-language summary
The tool generates a short written summary — two or three sentences — describing the current state. Something like: "Paid social spend is up 18% this week but conversion rate has dropped. Organic search is stable. Email performance is below the 4-week average."

This is the thing that saves the most time. The user can copy this into a Slack message or a client call prep doc without having to write it themselves.

---

## What It Doesn't Do (And Why)

I want to be explicit about what I'm leaving out of v1, because scope creep is where tools like this go wrong.

| What I'm leaving out | Why |
|---|---|
| Client-facing access/login | Adds trust, branding, and support overhead we don't need yet |
| Campaign-level drill-down | Channel-level is enough to answer the question; campaign detail is a separate use case |
| Recommendations or "what to do" | Generating trustworthy recommendations requires more context than the tool has; better to surface facts and let the analyst make the call |
| Historical trend charts | Useful eventually, but adds visual complexity and we need to establish the data layer first |
| Automated email/Slack delivery | Appealing, but push notifications require people to trust the data before they act on it; let's earn that trust first |
| Multi-user roles and permissions | One user type in v1: internal team |
| Real-time data | The complexity of live API calls isn't worth it at this stage; scheduled refreshes are fine |

---

## Data: Where Does It Come From?

This is honestly the hardest part of building this tool, and I want to be upfront about that.

The tool needs data from wherever the team currently tracks marketing performance. Based on a typical martech team setup, that probably includes some combination of:

- **Google Analytics / GA4** — for organic traffic and conversion data
- **Meta Business Suite / Ads Manager** — for paid social
- **Google Ads** — for paid search
- **HubSpot or similar CRM** — for email performance and lead data

All of these have APIs. In theory, the tool can connect to them directly. In practice, the reliability and complexity of those connections varies a lot.

**My v1 assumption:** The tool connects to whichever 2–3 platforms the team uses most heavily, and pulls data via their official APIs on a scheduled basis (e.g. every morning at 7am). The raw data lands in a simple data store (BigQuery or even a Google Sheet to start), and the tool reads from that.

This "pull to a store, then read from the store" pattern is important. It means the tool isn't dependent on live API calls at the moment someone opens it — it's always reading from a fresh but stable snapshot. If an API is down, the tool still works; it just shows last night's data.

**What I'm not solving in v1:** Connecting to every possible data source the team might use. Start with the top two or three channels, get that right, and expand from there.

---

## How a User Interacts With It

The interaction is intentionally minimal.

1. User opens the tool (a web app, simple enough to run in a browser)
2. Selects a client brand from a dropdown
3. Sees the performance snapshot for that brand — channel by channel, with delta indicators
4. Reads the auto-generated plain-language summary at the top
5. Optionally changes the date range (7 days vs. 30 days)
6. Done. The whole interaction takes under 2 minutes.

There's no login in v1 (it's an internal tool on a trusted network). There are no settings to configure. There is no way to add data or edit anything. The tool is read-only.

---

## What Would Make a User Trust It?

This is a question I kept coming back to, because a tool that people don't trust is worse than no tool at all — they'll just keep doing it manually.

A few things I think matter most:

- **Data timestamps are visible.** Every metric shows when it was last updated. No ambiguity about whether you're looking at yesterday's numbers or last week's.
- **The source is shown.** "Impressions (via Google Ads API)" is more trustworthy than just "Impressions." Users know where the number came from and can verify it if they want to.
- **Discrepancies are acknowledged, not hidden.** If a data source didn't update successfully, the tool says so explicitly rather than showing stale data silently.
- **The summary is transparent about what it's based on.** The plain-language summary should include which channels it's drawing from, so users know if something's been left out.

---

## Rough Data Flow

```
[Platform APIs]
      |
      v
[Scheduled Connector Scripts] — run every morning
      |
      v
[Central Data Store — BigQuery or Google Sheets]
      |
      v
[MPA Web App] — reads from store, generates summary
      |
      v
[User opens tool, sees snapshot]
```

The connectors are separate from the app. They run independently, fail independently, and log their status. This means if the Meta connector breaks, it doesn't take down the whole tool — users just see a "Meta data unavailable" notice.

---

## If I Had More Time

A few things I'd want to explore with more time or after v1 ships:

- **Natural language querying** — "Show me how Brand X performed on paid social last month vs. the month before." Right now the tool is fixed in what it shows; a query layer would make it much more flexible.
- **Anomaly detection** — Instead of simple delta flags, something smarter that accounts for seasonality, day-of-week effects, and campaign flight dates.
- **Slack integration** — Once users trust the data, a morning Slack digest would be genuinely useful. But we need to earn that trust first.
- **A proper client view** — With appropriate framing, context, and access control. This is the obvious v2.

---

## One Thing I'd Push Back On

The brief says "the team is not going to change the tools they use." I respect that constraint and I've scoped around it. But I'd want one conversation about data storage. If the team doesn't already have a central data warehouse, v1 will need somewhere to put the aggregated data. A BigQuery sandbox is free, easy to set up, and doesn't require anyone to change how they work — it just adds a layer that wasn't there before. That's worth raising.
