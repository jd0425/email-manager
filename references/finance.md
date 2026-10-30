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

## Matching a later email to an existing bill row

"Close the matching reminder" needs a definition, or one bill ends up with
two rows and two calendar reminders (a statement email and its "due in 3
days" email both look like a legitimate bill). Rules:

1. **One row per statement/due date**, not per account per month. Two
   separate bills from the same account in a month are two rows.
2. **Same `account`.** `account` is free text, so keep it consistent: use
   the payee's name, not the sender address, so a statement and a reminder
   from different addresses still match.
3. **A reminder or revised bill updates the existing row** (and its one
   calendar reminder) instead of adding another. It matches when it has
   the same account and amount, arrives on or after the row's `date_seen`,
   and is within ~45 days of its `due_date`.
4. **A payment applies to the oldest unpaid row** for that account with
   `date_seen` on or before the payment date, so past-due bills clear
   before the current cycle and a newer notice never takes a payment from
   an older open one. Look back no more than ~45 days from `due_date`.
5. **Exact amount** → fill `date_paid`, append the email id to `notes`,
   and leave `source_email_id` as the original bill.
6. **Less than the bill** → a partial payment. Append
   `partial $X on <date>` to `notes` and leave the row open; close it once
   the partials add up to the full amount. No balance column — this is not
   reconciliation.
7. **More than the bill, or fits no open row** → catalog it `needs_review`
   and list it in the digest. Never guess a match. (A re-send of a payment
   already recorded is a duplicate, rule 9, not a review item.)
8. **Each email closes at most one row.**
9. **Duplicates are not payments.** A payment email whose id is already in
   `notes`, or that has the same account, amount and payment date as a
   payment already recorded (full or partial), is a re-send. Note
   `duplicate of #<id>` and move on: no review item, and never add it to
   the partial total a second time.
10. **Pending is not paid.** A "pending", "scheduled" or "processing"
    email adds `pending $X on <date>` to `notes`. The row stays open and
    `date_paid` stays empty; the digest shows it as "payment pending"
    instead of due or overdue. A later reminder for the same bill only
    updates the row and does not change the pending status.
11. **"Received" or "posted" is the real payment.** It replaces the pending
    note for the same amount, so the payment is counted once.
12. **A pending note with no "received" email after ~7 days** is called
    out in the digest ("pending for N days, did it go through?"). The row
    stays open; don't assume it failed or succeeded.

Example: a $15.99 monthly subscription. In a backlog, March's receipt must
not close April's bill: it predates April's `date_seen`, and it closes only
the oldest unpaid row.

When a large backlog is split across subagents, a bill and its follow-up
emails can land in different chunks that can't see each other's rows. Run
this matching again when merging the scratch ledgers, not only per message.

Keep the scope narrow on purpose: this is "don't lose track of a bill
buried in an inbox," not a personal-finance app. If the user wants real
budgeting/reconciliation, that's a different tool — say so rather than
trying to stretch this ledger to cover it.
