# Catalog schema

`catalog.csv` — one row per email, ever. Never overwrite existing rows;
always append. Columns:

| Column | Meaning |
|---|---|
| `id` | The mail provider's message id (stable — lets you look the message up again later) |
| `date_received` | ISO date |
| `account` | *Optional.* Which mailbox this came from, only needed for a multi-account setup (see below) — omit the column entirely for a single-account setup |
| `from` | Sender address |
| `to_alias` | Which of the user's addresses/aliases received it (see `aliases.md`) — for aliases within *one* mailbox, not separate accounts (see `account` above) |
| `subject` | Subject line |
| `category` | One of the categories defined in `categories.md` for this workspace |
| `sub_action` | Which specific rule fired, e.g. `"not_a_fit"`, `"expired"`, `"auto_payment"`, `"food_delivery"` — free-form but consistent within a category |
| `status` | `cataloged` (seen, no action yet) / `kept` / `filed` (moved to a folder/label) / `pending_delete` (recommended, awaiting the user's approval) / `deleted` (moved to trash) / `spam` / `needs_review` |
| `review_needed` | `TRUE`/`FALSE` — surfaced in the daily digest if `TRUE` |
| `due_date` | For bills/todos, ISO date |
| `calendar_created` | `TRUE`/`FALSE` |
| `amount` | For bills/receipts, if present |
| `notes` | Free text — the reasoning behind the categorization, especially for anything non-obvious |

## Status defaults

- `pending_delete` is the default for anything not obviously safe to clear
  automatically (an ambiguous promo, a job lead that might matter, etc.).
- `deleted` (i.e. auto-trashed immediately, no human in the loop) is
  reserved for categories the user has explicitly confirmed are safe —
  see the Safety rules in `SKILL.md`. Don't default new categories to
  `deleted` without that confirmation.
- Misdirected mail (someone else's mail landing in this inbox because of a
  similar name/address) should get its own category, `status=needs_review`
  the first several times it shows up, so the user can confirm before you
  start auto-filing or auto-deleting those too.

## Multiple accounts

Two supported patterns for someone with more than one mailbox (a personal
Gmail and a work Gmail, say) — pick based on whether they want them managed
together or kept fully separate:

- **Separate workspace per account (default, simplest).** Run this whole
  skill once per account — its own `catalog.csv`, `ledger.csv`,
  `accounts.md`, and viewer, in its own folder, with its own MCP connector
  registration (see the "Multiple accounts" section in
  `references/setup.md`). No schema changes needed. Best when the two
  inboxes genuinely don't overlap (e.g. work mail should never be
  cross-referenced against personal mail).
- **One unified catalog with the `account` column.** Fill in `account` on
  every row (e.g. the mailbox's address) and point `scripts/build_viewer.py`
  at the combined `catalog.csv`. The viewer picks up an account filter and
  column automatically once more than one distinct value shows up in that
  column — a single-account catalog with the column omitted (or all one
  value) renders exactly as before. Best when the user wants one daily
  digest and one dashboard across everything.

Either way, this is a different problem from the backlog parallelization
in `SKILL.md`'s "Working through a large backlog" — that's splitting *one*
mailbox's backlog into chunks. Running one subagent per *account* (each
scoped to its own connector and, for the unified pattern, its own `account`
value) is a natural extension of the same parallel-subagent approach, and
the two can combine: one subagent per account, each of which may itself
split a large backlog into further chunks.

## Sizing note

This file grows without bound (append-only, one row per message ever
seen). That's intentional — it's the audit trail. If it gets large enough
that a full re-read becomes expensive, prefer scripts that stream/filter
it (e.g. `csv.DictReader` with a generator) over loading the whole thing
into a chat context.
