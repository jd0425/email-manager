# Mock bill emails (oldest first)

Accounts: StreamCo ($15.99 monthly, due the 5th), Lakeside Utilities,
Maple Water, Birchwood Insurance.

1. 2026-03-01 — StreamCo statement: $15.99 due 2026-03-05.
2. 2026-03-03 — StreamCo reminder: "$15.99 due in 2 days" (same bill as #1).
3. 2026-03-05 — StreamCo receipt: "Payment received, $15.99".
4. 2026-04-01 — StreamCo statement: $15.99 due 2026-04-05.
5. 2026-04-02 — Lakeside Utilities statement: $120.00 due 2026-04-20.
6. 2026-04-02 — Maple Water statement: $40.00 due 2026-04-30.
7. 2026-04-10 — Lakeside Utilities: "Payment received, $50.00" (payment date 2026-04-10).
8. 2026-04-12 — Lakeside Utilities: the same $50.00 receipt re-sent (payment date 2026-04-10).
9. 2026-04-18 — Lakeside Utilities: "Payment received, $70.00".
10. 2026-04-22 — Maple Water: "Payment pending, $40.00". No later email arrives.
11. 2026-04-25 — Lakeside Utilities: "Payment received, $300.00" (fits no open row).
12. 2026-04-26 — Birchwood Insurance statement: $80.00 due 2026-05-10.
13. 2026-04-28 — StreamCo re-sent receipt for the March payment ($15.99, payment date 2026-03-05). Must not close April's bill.
14. 2026-04-29 — Birchwood Insurance: "Payment pending, $80.00".
15. 2026-04-30 — Birchwood Insurance reminder: "$80.00 due in 10 days" (arrives after the pending email).
16. 2026-05-01 — Birchwood Insurance: "Payment received, $80.00".
