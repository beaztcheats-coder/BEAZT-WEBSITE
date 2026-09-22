"""Route smoke tests for the catalogue redesign (run with `uv run python tmp/validate_routes.py`)."""
import sys
sys.path.insert(0, ".")

from app import app  # noqa: E402  (import runs migrations + seed)
from models import db, User, Product, Review  # noqa: E402

failures = []


def check(cond, label):
    status = "ok" if cond else "FAIL"
    print(f"  [{status}] {label}")
    if not cond:
        failures.append(label)


with app.app_context():
    # Confirm the game column migration landed.
    conn = db.engine.raw_connection()
    cols = [r[1] for r in conn.cursor().execute("PRAGMA table_info(products)").fetchall()]
    conn.close()
    check("game" in cols, "products.game column exists after migration")
    check(
        db.engine.dialect.has_table(db.engine.connect(), "reviews") if hasattr(db.engine, "connect") else True,
        "reviews table presence check",
    )

client = app.test_client()

print("\n-- Route status checks --")
routes = [
    ("/", 200),
    ("/cheats", 200),
    ("/games", 200),
    ("/games/rust", 200),
    ("/games/does-not-exist", 404),
    ("/status", 200),
    ("/sitemap.xml", 200),
    ("/robots.txt", 200),
    ("/product/rust-external-private", 200),
    ("/product/nope", 404),
    ("/?game=rust", 200),
    ("/?sort=price-asc", 200),
    ("/?q=zzz-no-match", 200),
    ("/cheats?status=online", 200),
    ("/faq", 200),
    ("/admin/", 302),  # redirects to login
]
for path, expected in routes:
    r = client.get(path)
    check(r.status_code == expected, f"{path} -> {r.status_code} (want {expected})")

print("\n-- Content checks --")
r = client.get("/")
html = r.get_data(as_text=True)
check("Rust External - BeaZt Legit" in html, "homepage SSRs the product catalogue")
check("From &pound;9.00" in html or "From £9.00" in html, "homepage shows cheapest tier price")
check("/games/rust" in html, "homepage links the game landing page")
check("status-badge" in html, "homepage uses text status badges")
check("FULL STATUS BOARD" in html, "homepage links the full status board")
check("verified reviews" in html.lower() or "review" in html.lower(), "homepage reviews section renders")

r = client.get("/sitemap.xml")
xml = r.get_data(as_text=True)
check("<urlset" in xml, "sitemap is valid XML urlset")
check("/product/rust-external-private" in xml, "sitemap includes product URLs")
check("/games/rust" in xml, "sitemap includes game pages")
check("http://localhost:5000/robots" not in xml, "sitemap uses site URL")

r = client.get("/robots.txt")
robots = r.get_data(as_text=True)
check("Sitemap:" in robots, "robots.txt references sitemap")
check("Disallow: /admin" in robots, "robots.txt blocks /admin")

r = client.get("/games/rust")
html = r.get_data(as_text=True)
check("Rust" in html and "cheat-card" in html, "game page lists its products")

r = client.get("/status")
html = r.get_data(as_text=True)
check("Undetected" in html, "status board shows real statuses")
check("99.9%" not in html, "status board has no fabricated uptime")

r = client.get("/product/rust-external-private")
html = r.get_data(as_text=True)
check('application/ld+json' in html, "product page has JSON-LD structured data")
check('"aggregateRating"' not in html, "no aggregateRating without approved reviews")
check('rel="canonical"' in html, "product page has canonical link")
check('id="reviews"' in html, "product page has reviews section")

print("\n-- Review flow (DB-level) --")
with app.app_context():
    product = Product.query.filter_by(slug="rust-external-private").first()
    user = User.query.filter_by(is_admin=True).first()
    if not user:
        user = User(username="testreviewer", email="tr@example.com")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
    # Clean slate for this product/user.
    Review.query.filter_by(product_id=product.id).delete()
    db.session.commit()
    check(Review.query.filter_by(product_id=product.id).count() == 0, "no reviews initially")

    r = client.get("/")
    html = r.get_data(as_text=True)
    check("No verified reviews yet" in html, "homepage shows honest empty state with zero reviews")

    rev = Review(
        user_id=user.id, product_id=product.id, rating=5,
        title="Solid", body="Works exactly as described, setup was quick.",
        status="pending",
    )
    db.session.add(rev)
    db.session.commit()

    r = client.get("/")
    html = r.get_data(as_text=True)
    check("Solid" not in html, "pending review is NOT shown publicly")

    rev.status = "approved"
    db.session.commit()
    r = client.get("/")
    html = r.get_data(as_text=True)
    check("Solid" in html, "approved review is shown on homepage")

    r = client.get("/product/rust-external-private")
    html = r.get_data(as_text=True)
    check('"aggregateRating"' in html, "aggregateRating appears with approved reviews")
    check("Verified buyer" in html, "review marked as verified buyer")

    # Admin moderation routes exist and guard access.
    r = client.get("/admin/reviews")
    check(r.status_code == 302, "admin reviews requires login")

print()
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("ALL CHECKS PASSED")
