# Example category rules — fork and customize

These rules come from one real deployment (a job-searching professional's
Gmail). They're a *starting template*, not a spec — walk through them with
whoever you're setting this up for, keep what applies, and replace the rest
with their actual inbox's shape. The pattern each category follows is more
important than the specific example: **what is this kind of message, and
what should happen to it by default?**

### Leads / opportunities (e.g. job postings, if job-searching)

- Compare against the user's own criteria (resume/profile, if they've given
  you one; otherwise ask what "a fit" looks like for them) for a
  fast reject/strong-fit signal.
- Fit → surface in the daily digest, create a to-do with a due date (from
  the email if given, otherwise a sensible default).
- Not a fit → `deleted`, with the reason noted in the catalog. The user can
  always reverse a call from the catalog.
- Past its relevance window with no action taken → `deleted`.
- If the user already has a separate, dedicated system for pursuing these
  leads (a tracker, another automation), this category's job is just to
  clear the inbox, not to re-decide fit — log it, then clear it, and only
  flag something for review if it clearly ties back to something already
  being actively pursued elsewhere.
- Digest-style emails that bundle several items in one message (can't
  judge from the subject alone) → `needs_review` rather than guessing at
  the contents.
- A message from an individual (not a platform/aggregator) → `needs_review`,
  and note if anything about it conflicts with a stated preference (e.g.
  location, timing). If the same message arrives twice within minutes,
  note it as a duplicate rather than double-cataloging it as new signal.
- Spam / spam-adjacent → `spam` (implies delete), and actually mark it as
  spam with the provider so its filter learns. **Exception: don't mark a
  platform the user actively relies on as spam** just because one message
  from it is low-value — a generic nudge from a platform they get real
  value from is routine, not spam. Doing so risks burying real signal from
  a source they depend on.

### Promotions / marketing

- Expired offer → `deleted`.
- Doesn't match anything in the user's actual purchase/account history →
  `deleted`.
- Anything genuinely worth a look → surface in the digest, not just the
  catalog.
- Long-term goal: track unsubscribe candidates (`unsubscribe_candidates.md`)
  and eventually recommend/automate unsubscribing from low-value senders.
- A promo tied to a *known* account (see `accounts.md`) is still routine —
  `deleted` is fine — but confirms the account relationship, so log it
  there even though the email itself gets cleared.
- Consider a review-first model (hold for a short window before
  auto-deleting) once the user trusts the categorization, rather than
  immediate auto-delete from day one.

### Bills

- Legitimate bill → note amount + due date in the catalog and in
  `finance/ledger.csv`, create a calendar reminder to pay, timed
  reasonably ahead of the due date.
- A "payment received"/receipt email that arrives after → close out the
  matching reminder rather than creating a new one.

### Delivery / shipping notices

- Note briefly in the catalog, then `deleted`. Routine delivery
  confirmations (food delivery, package tracking) usually don't need more
  than the catalog row.

### Accounts (banking, utilities, loans, insurance, subscriptions, etc.)

- The first time an account/institution is seen, record it in
  `accounts.md` — across *every* category, not just ones explicitly about
  accounts. A promo email from a bank still confirms the account exists,
  so log it there even while the email itself gets `deleted` as routine
  marketing. Mark anything inferred-but-not-confirmed as "unconfirmed"
  until a second signal corroborates it (a real statement, a bill).
- Standard recurring payments → calendar reminder as in Bills; brief note,
  then `deleted`.
- **Employer info**, if relevant: delete routine/old employer email; keep
  offers, job descriptions, and login/help-desk info, filed into a
  dedicated folder rather than deleted.

### Appointments (haircuts, dentist, any recurring personal booking)

- Create a calendar entry, then `deleted`.
- Track known providers/booking platforms as they come up (this is
  useful signal for `accounts.md` too, even for a non-financial account).

### Learning

- Note the user's actual interests once known, and surface anything
  relevant in the digest. Clean up old/expired course-promo email.

### Entertainment / subscriptions / games

- If the user asked for a specific notification (pre-order, restock,
  release alert), surface it.
- If something they follow is returning/renewing, note it.
- Otherwise, delete after noting. Watch for subscription-renewal emails
  specifically (these often matter even when the platform's routine
  marketing doesn't).

### Receipts (transactional, not marketing)

Providers sometimes file pure transactional mail (payment processing,
order confirmation) under a marketing/promotions label alongside actual
ads. Recognize these — "your payment is processing," "your order
confirmation" — and catalog as `category=receipt`, not `promotion`.
Routine/small purchases → `deleted` like any other low-stakes category;
don't log every minor purchase to the ledger, only recurring bills or
amounts worth tracking (judgment call — note the reasoning either way).

### Other (doesn't fit an existing bucket)

One-off things — a genuinely novel request, a survey, something that
doesn't map to any category above — don't force them into one.
`category=other`, `status=needs_review`, clear note. If a pattern of
these starts showing up, that's a sign to add a real category instead of
leaving them all as `other`.
