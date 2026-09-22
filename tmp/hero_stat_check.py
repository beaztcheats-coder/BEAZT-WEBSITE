"""Verify hero stats render uniformly (value above label, no label-top modifier)."""
import re
import sys

sys.path.insert(0, r"E:\github\rust beazt\BEAZT-WEBSITE")

from app import app

with app.test_client() as c:
    resp = c.get("/")
    assert resp.status_code == 200, f"homepage returned {resp.status_code}"
    html = resp.get_data(as_text=True)

assert "hero-stat--label-top" not in html, "label-top modifier still rendered"

stats = re.findall(
    r'<div class="hero-stat">\s*'
    r'<span class="hero-stat-val"[^>]*>([^<]+)</span>\s*'
    r'<span class="hero-stat-label">([^<]+)</span>',
    html,
)
assert len(stats) == 4, f"expected 4 uniform hero stats, found {len(stats)}: {stats}"

for value, label in stats:
    print(f"  OK  {value:<8} {label}")

print("HERO STATS UNIFORM: PASS")
