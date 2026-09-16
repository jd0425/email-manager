#!/usr/bin/env python3
"""Rebuild viewer.html (the catalog viewer) from catalog.csv.

Self-hosting: the existing viewer.html is its own template. This script swaps
in a fresh catalog-data JSON payload and updates the header counts / NEWEST
anchor / category, status, and account dropdown options, then rewrites
viewer.html in place. It never hand-builds HTML strings for the data itself
— only the small surrounding chrome (stat numbers, option lists) gets
patched via regex against known anchor points in the template.

Usage:  python3 build_viewer.py [path/to/catalog.csv] [path/to/viewer.html]
Defaults to catalog.csv and viewer.html next to this script if not given.
Then redeploy viewer.html wherever the user views it (a hosted artifact, a
local file they open in a browser, whatever fits the runtime this skill is
used in). If the hosting mechanism supports redeploying to a stable URL,
prefer that over minting a new URL every batch.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CATALOG = os.path.join(os.path.dirname(HERE), "email", "catalog", "catalog.csv")
DEFAULT_VIEWER = os.path.join(os.path.dirname(HERE), "assets", "viewer.html")


def load_rows(catalog_path):
    out = []
    with open(catalog_path, newline="", encoding="utf-8") as f:
        for d in csv.DictReader(f):
            out.append({
                "id": d.get("id", ""),
                "d": d.get("date_received", ""),
                "acct": d.get("account", ""),
                "f": d.get("from", ""),
                "a": d.get("to_alias", ""),
                "s": d.get("subject", ""),
                "c": d.get("category", ""),
                "sa": d.get("sub_action", ""),
                "st": d.get("status", ""),
                "rv": d.get("review_needed", "").strip().upper() == "TRUE",
                "due": d.get("due_date", ""),
                "amt": d.get("amount", ""),
                "n": d.get("notes", ""),
            })
    return out


def main():
    catalog_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CATALOG
    viewer_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_VIEWER

    if not os.path.exists(viewer_path):
        sys.exit(f"{viewer_path} not found — need an existing copy to use as the template "
                  "(start from assets/viewer.html in this skill)")
    if not os.path.exists(catalog_path):
        sys.exit(f"{catalog_path} not found")

    rows = load_rows(catalog_path)
    if not rows:
        sys.exit("catalog.csv has no rows — nothing to build")

    dates = sorted(x["d"] for x in rows if x["d"])
    oldest, newest = dates[0], dates[-1]
    total = len(rows)
    needs_review = sum(1 for x in rows if x["st"] == "needs_review")
    auto_cleared = sum(1 for x in rows if x["st"] == "deleted")
    cats = sorted(set(x["c"] for x in rows if x["c"]))
    statuses = sorted({x["st"] for x in rows if x["st"]})
    accounts = sorted(set(x["acct"] for x in rows if x["acct"]))

    s = open(viewer_path, encoding="utf-8").read()

    js = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    s = re.sub(r'(<script id="catalog-data" type="application/json">)(.*?)(</script>)',
               lambda m: m.group(1) + js + m.group(3), s, count=1, flags=re.S)

    s = re.sub(r"var NEWEST = new Date\('[^']+'\);",
               "var NEWEST = new Date('%sT00:00:00');" % newest, s, count=1)

    s = re.sub(r'<div class="meta" id="headerMeta">.*?</div>',
               '<div class="meta" id="headerMeta">{:,} messages cataloged &middot; {} &ndash; {}</div>'.format(
                   total, oldest, newest),
               s, count=1)

    s = re.sub(r'<div class="n" id="statTotal">[\d,]*</div>',
               '<div class="n" id="statTotal">{:,}</div>'.format(total), s, count=1)
    s = re.sub(r'<div class="n" id="statReview">\d*</div>',
               '<div class="n" id="statReview">{}</div>'.format(needs_review), s, count=1)
    s = re.sub(r'<div class="n" id="statCleared">\d*</div>',
               '<div class="n" id="statCleared">{}</div>'.format(auto_cleared), s, count=1)

    cat_opts = "".join('<option value="%s">%s</option>' % (c, c.replace("_", " ")) for c in cats)
    s = re.sub(r'(<option value="">All categories</option>\s*)(?:<option value="[^"]+">[^<]+</option>)*',
               lambda m: m.group(1) + cat_opts, s, count=1)

    opt_order = ["needs_review", "pending_delete", "deleted", "kept", "filed", "spam", "cataloged"]
    opts = "".join('<option value="%s">%s</option>' % (o, o) for o in opt_order if o in statuses)
    s = re.sub(r'(<option value="">All statuses</option>\s*)(?:<option value="[^"]+">[^<]+</option>)*',
               lambda m: m.group(1) + opts, s, count=1)

    acct_opts = "".join('<option value="%s">%s</option>' % (a, a) for a in accounts)
    s = re.sub(r'(<option value="">All accounts</option>\s*)(?:<option value="[^"]+">[^<]+</option>)*',
               lambda m: m.group(1) + acct_opts, s, count=1)

    open(viewer_path, "w", encoding="utf-8").write(s)
    print("wrote", viewer_path)
    print("total=%d  range=%s..%s  needs_review=%d  auto_cleared=%d  categories=%s%s" %
          (total, oldest, newest, needs_review, auto_cleared, ", ".join(cats),
           "  accounts=" + ", ".join(accounts) if accounts else ""))


if __name__ == "__main__":
    main()
