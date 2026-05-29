# V1 Scope: What's In, What's Out, and Why

This document is meant to be a quick reference — something you can point to in a meeting when someone asks "but can it also do X?" The answer is usually no, and this explains why that's a deliberate choice.

---

## In Scope for V1

These are the things I'm committing to for the first version. They are enough to genuinely solve the problem as stated, without overbuilding.

| Feature | Description |
|---|---|
| Brand/client selector | Dropdown to switch between brands. Single-brand view at a time. |
| Channel performance snapshot | Key metrics per channel (impressions, clicks, spend, conversions, cost-per-result) |
| Period comparison | Default: last 7 days vs. prior 7 days. Toggle to 30-day view. |
| Delta indicators | Show % change per metric vs. prior period. Flag significant changes visually. |
| Plain-language summary | Auto-generated 2–3 sentence overview of current performance state |
| Data source labels | Each metric shows which platform it came from and when it was last refreshed |
| Failed data source notice | If a connector didn't update, say so clearly — don't show stale data silently |
| Scheduled data refresh | Connectors run once daily (morning). Data is always from the most recent successful pull. |
| Read-only interface | No editing, no settings, no accounts. Just read. |

---

## Out of Scope for V1

I want to be honest about this section. Most of these things are not out of scope because they're unimportant. They're out of scope because adding them to v1 would make it harder to ship, harder to trust, and harder to learn from.

| Feature | Why It's Out of Scope |
|---|---|
| Client-facing access | Requires branding, auth, and data trust that we haven't established yet |
| Campaign-level drill-down | Channel-level is what answers the question. Adding campaigns adds complexity without changing the answer to the core question. |
| Automated delivery (Slack/email) | Push notifications require people to already trust the data. Earn trust first, automate later. |
| Historical trend charts | Useful, but adds visual and data complexity. The summary + delta achieves 80% of the value. |
| Recommendations / "what to do" | The tool can tell you what happened. It shouldn't pretend to know what to do about it — that requires context it doesn't have. |
| Multi-user roles/permissions | Everyone on the team is a trusted internal user in v1. |
| Real-time / live data feeds | Adds API complexity and cost. Daily refresh is more than sufficient for the use case. |
| Cross-brand comparison views | Useful eventually, but adds complexity to the query layer. One brand at a time for now. |
| Custom date range picker | 7-day and 30-day toggles cover 90% of use cases. A full date picker adds UI complexity for minimal gain. |
| Mobile optimization | Internal tool, likely used at a desk. Not the priority right now. |

---

## The Guiding Principle Behind These Decisions

Every time I added something to the "out of scope" list, I asked one question:

> *Does this need to exist for someone to get value from the tool on day one?*

If the answer was no, it went out. The goal of v1 is to solve the stated problem — "answer the marketing performance question faster and more consistently" — not to become a comprehensive analytics platform.

A tool that does three things well is more useful than a tool that does ten things poorly. And it's much easier to add features to a working, trusted tool than to fix a broken one that tried to do too much.

---

## What I'd Revisit First After V1

If v1 ships and people use it, here's my rough priority order for what comes next:

1. **Slack/email digest** — once data trust is established, push delivery is the logical next step
2. **Campaign-level drill-down** — the next most common follow-up question after "how are we doing overall?" is "which campaigns specifically?"
3. **Historical trend view** — once we've been collecting data for 4–8 weeks, a simple trend chart becomes genuinely useful
4. **Client-facing view** — this is the real commercial opportunity, but it needs to be done properly

---

## Open Questions I'd Want to Resolve Before Building

1. **Which platforms does the team actually use?** I've assumed Google Analytics, Meta Ads, and Google Ads. That might be wrong. The connector list depends entirely on this.

2. **Is there already a data warehouse?** If the team already uses BigQuery, this is easier. If not, where should the aggregated data live?

3. **Who owns the API credentials?** Connecting to platform APIs requires someone to authorize access. Who is that person and how quickly can they do it?

4. **What counts as a "significant" change?** I've assumed a 10% delta is worth flagging. That might be too sensitive or not sensitive enough depending on the brand and channel. Worth discussing.

5. **How do we handle brands with different active channels?** Brand A might run paid social but not paid search. The tool needs to handle this gracefully — show what's available, indicate what isn't connected.
