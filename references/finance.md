# Finance capture

`finance/ledger.csv` — a running log of bills/receipts/payments seen in
email (due date, amount, date paid, category, account). This is
best-effort capture going forward from whenever the workspace starts, not
a full reconciliation of historical finances — don't try to backfill years
of history from it, and don't present it to the user as a complete
financial picture.

Suggested columns: `date_seen, due_date, amount, date_paid, category,
account, source_email_id, notes`. Adjust to fit what the user actually
wants tracked.

Also watch for, and at least call out in the daily digest even if they
don't go straight into the CSV:

- **Paycheck stubs** — if the user wants a starting snapshot once email
  access goes live, pulling together the last several weeks is a
  reasonable one-time bootstrap; ask before doing this rather than
  assuming.
- **Investment statements/confirmations** (brokerage, retirement accounts,
  etc.) — keep the emails (file, don't delete), and note the account +
  statement period in a dedicated `investments.md` once the first one
  shows up. Don't put investment balances in `ledger.csv` — that file is
  for bills/payments, not portfolio tracking.

Keep the scope narrow on purpose: this is "don't lose track of a bill
buried in an inbox," not a personal-finance app. If the user wants real
budgeting/reconciliation, that's a different tool — say so rather than
trying to stretch this ledger to cover it.
