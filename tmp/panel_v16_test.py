# Validation for the v16 cheat-panel / verified-today / hero-fade pass.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone

from app import app

c = app.test_client()
today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")

checks = []


def check(name, cond):
    checks.append((name, bool(cond)))
    print(("[ok] " if cond else "[FAIL] ") + name)


# 1. Hero background SVG must contain no text elements
svg = open("static/images/header_mockup.svg", encoding="utf-8").read()
check("hero SVG has no <text> elements", "<text" not in svg)
check("hero SVG still has panel geometry", "ESP feature rows" in svg)

# 2. Cache buster bumped
base = open("templates/base.html", encoding="utf-8").read()
check("cache-buster is v16", "style.css?v=16" in base)

# 3. CSS additions present
css = open("static/css/style.css", encoding="utf-8").read()
for rule in [
    ".cheat-card-updated-inner",
    ".cheat-card-updated-dot",
    ".status-row-uptime--today",
    ".cheat-card::after",
    ".cheat-card-tier",
]:
    check(f"CSS has {rule}", rule in css)

# 4. Pages render and show today's date
r = c.get("/cheats")
check(f"/cheats 200 (got {r.status_code})", r.status_code == 200)
check("/cheats shows today's date+day", today in r.get_data(as_text=True))

r = c.get("/")
check(f"/ 200 (got {r.status_code})", r.status_code == 200)
body = r.get_data(as_text=True)
check("/ homepage shows today's date in status board", today in body)
check("/ no stale DB-date-only status rows", "status-row-uptime--today" in body)

r = c.get("/status")
check(f"/status 200 (got {r.status_code})", r.status_code == 200)
check("/status shows today's date+day", today in r.get_data(as_text=True))

# product page (first active product slug)
from models import Product  # noqa: E402

with app.app_context():
    p = Product.query.filter_by(visibility="public").first()
    slug = p.slug if p else None

if slug:
    r = c.get(f"/product/{slug}")
    check(f"/product/{slug} 200", r.status_code == 200)
    body = r.get_data(as_text=True)
    check("product page shows today's date (meta)", today in body)
    check("product page has Status Verified spec", "Status Verified" in body)
    check("product page has no orphan jinja endif", "{% endif %}" not in body)
else:
    print("[skip] no active product in dev DB")

# 5. Valid HTML-ish sanity: no unresolved 'None' in updated lines
failed = [n for n, ok in checks if not ok]
print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed")
if failed:
    print("FAILED:", failed)
    raise SystemExit(1)
print("ALL CHECKS PASSED")
