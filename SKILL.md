---
name: email-manager
description: Turns Claude into a personal executive assistant that triages an email inbox into a durable, reviewable catalog — categorizing messages, auto-clearing routine clutter, flagging anything ambiguous, tracking bills into a finance ledger, and building a sortable/filterable HTML log of everything it touched. Use this skill whenever the user wants help cleaning up, organizing, or triaging their inbox, mentions "inbox zero," a recurring email backlog, wants bills or recurring accounts tracked automatically from email, wants a daily inbox digest, or wants to set up a personal/executive-assistant-style email workflow with Claude — even if they don't use the word "skill" or name this workflow directly. Also use it when the user asks to set up, configure, or troubleshoot Gmail/Calendar access for Claude via an MCP server.
---

# Email Manager

This skill turns inbox triage into a repeatable, auditable workflow instead of
a one-off cleanup: every message gets logged to a CSV catalog before any
action is taken, routine clutter gets cleared automatically, anything
ambiguous gets flagged for the user instead of guessed at, and bills/known
accounts get captured into simple running logs. The point isn't to be clever
per-message — it's to build a system the user trusts enough to hand off real
autonomy to over time.

**This is a template, not a finished product.** The category rules below are
examples from a real deployment (a job-searching professional's Gmail). The
first time you use this skill for someone, walk them through customizing the
categories, accounts, and thresholds to their own inbox — don't just run the
example rules against a stranger's email. Save what you learn about their
preferences back into this file (or a workspace-local copy of it) as you go,
the same way you'd refine any standing instruction set.

## Prerequisite: email/calendar access

This skill works two ways — pick whichever matches how much setup the user
wants to do before seeing value:

- **No-connector fallback (the standard first option).** The user exports or
  forwards a batch of email (a `.mbox`/`.eml` export, a handful of forwarded
  messages, or pasted text) with no MCP or API access required. This has a
  real advantage, not just a lower bar: it works immediately, for anyone,
  regardless of provider, and it's a good way to demo the catalog/triage
  workflow on a sample batch before committing to live account access. Run
  the same batch-triage procedure below against whatever was exported —
  everything downstream (categorization, the catalog, the viewer) is
  identical either way. Its limits: no bulk mailbox actions (archiving,
  labeling), no live pagination through a real inbox, and no calendar
  writes, so bills/appointments get logged to the catalog and ledger but not
  turned into live reminders. Say this limit out loud when suggesting the
  fallback, and offer the live-connector path as the natural next step once
  the user has seen the workflow work on their own mail.
- **Live connector (for ongoing, hands-off use).** An MCP server that can
  read, label, and file email (Gmail in the reference implementation, via
  the open-source Google Workspace MCP server) plus a calendar. If that's
  not set up yet, read `references/setup.md` and walk the user through it —
  don't try to fake this with a "describe what you'd do" answer. If a
  different mail provider is in play, adapt the setup steps to whatever MCP
  or API is available for it; the rest of this skill doesn't care which
  provider is behind the tool calls.

**Scope the permissions deliberately.** The reference setup grants read +
organize (label/archive/trash) + compose-draft, but deliberately *not*
send. Claude can file things and prep a reply, but a human hits send. Flag
this tradeoff to the user rather than silently requesting broader scopes.

## First-time setup with a new user

Before triaging anything, get explicit answers to:

1. **Categories.** What kinds of email actually show up in this inbox, and
   what should happen to each — auto-clear, file, flag for review, log to
   the ledger, create a calendar reminder? Start from the example category
   list in `references/categories.md`, but expect to add/remove/rename
   categories for this person's actual inbox (a student's categories look
   nothing like a small-business owner's).
2. **What "safe to auto-delete" means to them.** Be conservative by
   default — see Safety rules below — and let the user loosen it later
   once they've seen the catalog and trust the judgment calls.
3. **Known accounts/institutions worth tracking** (bank, utilities, auto
   loan, employer, subscriptions) — seed `accounts.md`, but expect this to
   grow as new senders show up.
4. **Aliases** — every address that lands in *this one inbox*, so
   misdirected mail for someone else with a similar name/address doesn't
   get acted on as if it were theirs. (This is different from having
   *multiple separate mailboxes* — see "Multiple accounts" below.)
5. **How many mailboxes.** One, or several (e.g. personal + work)? If more
   than one, see "Multiple accounts" below before setting up connectors.

Write the answers into workspace copies of the reference files (don't edit
the bundled `references/` copies in place — treat them as the starting
template each new setup forks from).

## Safety rules (non-negotiable defaults)

- **No permanent deletes without approval.** "Delete" means moving to
  trash (recoverable), never a permanent purge. Reserve a
  `pending_delete` status for anything not obviously safe, and only use
  an immediate `deleted` status for categories the user has explicitly
  confirmed are safe to auto-clear.
- **Never silently skip a message.** If a message is ambiguous, catalog it
  as `needs_review` rather than guessing at intent.
- **Log before you act.** Write the catalog row for a message before (or
  in the same step as) taking any action on it, so the catalog is always
  the true record of what happened, not a reconstruction after the fact.

## The catalog

`catalog.csv` is the source of truth — one row per message, ever. See
`references/schema.md` for the exact columns and status values. Corrections
happen by the user telling Claude in chat, which updates the CSV (and the
mailbox, and ideally a git commit if the workspace is versioned) — the
catalog stays the single source of truth rather than something the user
edits by hand.

## Batch triage procedure

This is the loop validated against real inbox behavior — reuse it rather
than improvising a different approach per session:

1. Search the mailbox scoped to one manageable chunk at a time (a label, a
   date range, a provider-side category) at a reasonable page size. Note
   the pagination cursor immediately — it's the resume point if the
   session ends mid-batch.
2. Fetch **metadata only** where possible (sender, subject, date, labels) —
   full message bodies are usually unnecessary for triage and much more
   expensive to pull. Only fetch a full body when metadata genuinely isn't
   enough to categorize.
3. Categorize every message against the user's rules (start from
   `references/categories.md`, customized per step "First-time setup"
   above). Watch for messages that a provider mis-bucketed (e.g. an actual
   bill showing up under a "promotions" label) — categorize by what the
   message *is*, not by where the provider filed it.
4. Write catalog rows with a small script using a real CSV writer (handles
   quoting, commas, emoji correctly) — don't hand-write CSV rows as
   strings, that's how catalogs get silently corrupted. Append, don't
   overwrite.
5. Take the bulk action for anything with an auto-clear status in one
   batched call rather than one-by-one, if the mail API supports it.
   Leave anything `needs_review` untouched until the user weighs in.
6. Rebuild the catalog viewer (`scripts/build_viewer.py`) and update
   `accounts.md` / `aliases.md` / any "worth unsubscribing from" notes
   with anything new noticed along the way.
7. If a category isn't fully processed by the end of a session, write the
   resume point (pagination cursor, *and* a token-free fallback like a
   date cutoff, since cursors aren't always durable) into the workspace
   README before ending.

### Working through a large backlog

A first run against a real inbox is often hundreds or thousands of unread
messages, not a handful — don't process it as one giant undifferentiated
batch and don't quietly stop after the first chunk. Split the backlog into
chunks along a natural boundary (a date range, a label, a sender domain) and
work through them as a checklist, updating the resume point after each one.

If the runtime this skill is used in supports spinning up parallel
subagents, use that for a large backlog: assign each subagent one
independent chunk (a disjoint date range or label, never overlapping — two
subagents categorizing the same message is how the catalog gets duplicate
or conflicting rows) with the categorization rules and catalog schema
inline in its instructions, have each one append to its own scratch CSV
rather than writing `catalog.csv` directly, then merge the scratch files
into the real catalog and rebuild the viewer once, after all chunks report
back. Give the user a single consolidated report at the end — total
processed, breakdown by category and by action taken, and everything
flagged `needs_review` — rather than one report per chunk; a wall of
per-subagent status updates is harder to act on than one summary.

**This is not the same thing as multiple email accounts.** The above splits
*one* mailbox's backlog into chunks. A user with several separate mailboxes
(personal + work, say) is a different setup question — see "Multiple
accounts" in `references/schema.md` and `references/setup.md` for how to
register a connector per account and, optionally, extend the catalog with
an `account` column. The two do combine: one subagent per account, each of
which may itself split a large backlog into further chunks.

## Bills and the finance ledger

See `references/finance.md`. In short: capture recurring bills and
noteworthy receipts into `ledger.csv` as they're seen in email (best-effort,
not full reconciliation), and create a calendar reminder for anything with a
due date. When a "payment received" confirmation shows up later, close out
the existing reminder rather than creating a duplicate.

## The catalog viewer

A single self-contained HTML file (`assets/viewer.html`, rebuilt by
`scripts/build_viewer.py`) gives the user a sortable/filterable view of the
catalog instead of raw CSV — stat cards, category chips, a status filter,
and a table. It's a snapshot, not live: rebuild and redeploy it after every
batch. If the runtime this skill is used in has a way to publish
self-contained HTML pages persistently (e.g. an Artifact-style tool), prefer
redeploying to the *same* URL each time over creating a new one per batch —
keep the link stable so the user can bookmark it once.

Read-only by design: corrections happen by the user talking to Claude, which
updates `catalog.csv` (and the mailbox) as the source of truth. Only build
an editable viewer if chat-based correction turns out to be a real
bottleneck in practice — it usually isn't.

## Daily digest

After a working session, produce a short digest:

- **Stats** — volume processed by category, how much was auto-cleared vs.
  filed vs. flagged.
- **Needs the user's eyes** — anything flagged `needs_review`, bills due
  soon, anything time-sensitive.
- **Not** a re-list of everything auto-cleared — the catalog is the full
  record; the digest is the highlights.

## Working style

- **First pass on a new inbox (or a new category) is collaborative.**
  Narrate judgment calls to the user as they come up rather than acting
  fully autonomously — this is how you calibrate what "safe to auto-clear"
  actually means for this person.
- **Move toward autonomy only after the rules have been validated** against
  real inbox behavior for a while. When the user corrects a call, fold the
  correction back into the category rules (in the user's workspace copy)
  so the same mistake doesn't repeat.
- **Keep the inbox itself down to actionable items only** — everything else
  gets filed into folders/labels, not left sitting in the inbox unsorted.
  Default to a few high-level folders; only get more granular where it
  actually earns its keep (e.g. a single employer worth its own folder,
  but generic promotions don't need ten sub-folders).

## Automating this over time

Once the rules have been validated collaboratively and the user trusts the
judgment calls (see Working style above), the natural next step is turning
this from something the user has to ask for into a recurring routine —
triage runs on its own schedule and the user just reads the digest.

Don't reach for this on day one, and don't build it before the categories
and safety thresholds have actually been exercised against real inbox
behavior for a while — an automated run repeats mistakes just as
efficiently as it repeats good calls. When the user is ready:

- Use whatever recurring/scheduled-task mechanism the current runtime
  provides for firing a fresh session on a timer (for example, a daily
  scheduled task that runs the batch triage procedure and finance-ledger
  step, then produces the daily digest as its output) — describe this
  generically here since the exact mechanism is runtime-specific, and use
  whichever real scheduling tool is available rather than an ad hoc
  in-process timer that won't survive past the current session.
- Keep the schedule conservative at first (e.g. once a day) and keep the
  same safety rules in force — a scheduled run gets no free pass on
  permanent deletes or on acting on anything ambiguous.
- Have the scheduled run end by delivering the daily digest to the user
  (however this runtime delivers messages/notifications) rather than
  silently updating the catalog with nothing to show for it — the digest is
  what keeps the automation legible.
- If a scheduled run hits something it isn't confident about (a new sender,
  a category it hasn't seen, anything outside the validated rules), it
  should flag it as `needs_review` and keep going rather than stopping the
  whole run to ask — a human isn't necessarily there to answer.

## Possible extensions (not built here)

- **Finance/bills dashboard.** `ledger.csv` (see Bills and the finance
  ledger above) is currently a plain log, not a viewer. The same pattern
  used for the catalog viewer — a single self-contained HTML file rebuilt
  from the CSV by a small script — extends naturally to a bills/spending
  view (upcoming due dates, recurring-amount trends, paid-vs-pending
  status). This is a natural v2, not something to build as part of a first
  setup; treat it the way `assets/viewer.html` was treated here — a
  separate asset and script pair, added once the ledger itself has real
  data and the user actually wants a dashboard rather than just the raw
  CSV.

## Reference files

- `references/setup.md` — configuring Gmail/Calendar MCP access from
  scratch (OAuth app, permission scopes, re-auth troubleshooting, and
  registering a separate connector per account for multiple mailboxes).
- `references/schema.md` — the `catalog.csv` column reference, including
  the optional `account` column and the two supported multi-account
  patterns.
- `references/categories.md` — example category rules to fork and
  customize (job leads, promotions, bills, deliveries, accounts,
  appointments, learning, entertainment, receipts, and a catch-all).
- `references/finance.md` — the `ledger.csv` format and what to capture.
- `scripts/build_viewer.py` — regenerates `assets/viewer.html` from
  `catalog.csv`. Run it, don't hand-edit the viewer's data.
- `assets/viewer.html` — the clean starting template for the catalog
  viewer (empty state — `build_viewer.py` populates it).
