# Changelog

## v0.2.0 — 2026-10-30

Bill matching in the finance ledger (issue #1, PR #2; thanks @mattabate).

- `references/finance.md`: "Matching a later email to an existing bill row" now defines what "the matching reminder" means.
  - One row per statement/due date; a payment applies to the oldest unpaid row for the account; each email closes at most one row.
  - A reminder or revised bill updates the existing row and calendar reminder instead of adding another.
  - Partial payments are logged in `notes` and close the row when they sum to the bill; anything that fits no open row goes to `needs_review`.
  - Re-sent receipts are duplicates and are never counted twice.
  - "Pending"/"scheduled" emails are notes, not payments; "received" replaces them; a pending note with no follow-up after ~7 days is flagged in the digest.
- Subagent backlog merge re-runs the matching over merged ledger scratch files.
- `evals/`: eval 4 (16 mock emails) covers the monthly-subscription boundary, partials, duplicates and pending → received.

## v0.1.0

Initial release.
