"""End-to-end review submission test (run with `uv run python tmp/review_flow_test.py`)."""
import sys
sys.path.insert(0, ".")

from app import app
from models import db, User, Product, Review, Key

with app.app_context():
    Review.query.delete()
    db.session.commit()

client = app.test_client()
with client.session_transaction() as s:
    s["_csrf_token"] = "testtoken123"
    s["_user_id"] = "1"
    s["_fresh"] = True

with app.app_context():
    user = db.session.get(User, 1)
    product = Product.query.filter_by(slug="rust-external-private").first()
    from routes.main import _user_can_review
    print("eligible (should be False, no orders/keys):", _user_can_review(product, user.id))

    r = client.post("/product/rust-external-private/review", data={
        "csrf_token": "testtoken123", "rating": "5", "body": "This is a real test review body."})
    print("ineligible POST ->", r.status_code, "(want 302)")
    print("review rows after ineligible POST:", Review.query.count(), "(want 0)")

    k = Key(user_id=user.id, product_id=product.id, key_value="TEST-KEY-REVIEW-1", is_active=True)
    db.session.add(k)
    db.session.commit()

    r = client.post("/product/rust-external-private/review", data={
        "csrf_token": "testtoken123", "rating": "5", "title": "Great", "body": "This is a real test review body."})
    print("eligible POST ->", r.status_code, "(want 302)")
    rev = Review.query.first()
    print("review created:", bool(rev), "| status:", rev.status if rev else None, "(want pending)")

    client.post("/product/rust-external-private/review", data={
        "csrf_token": "testtoken123", "rating": "4", "body": "Second review attempt here."})
    print("duplicate blocked:", Review.query.count() == 1, "(want True)")

    Review.query.delete()
    db.session.commit()
    r = client.post("/product/rust-external-private/review", data={
        "csrf_token": "testtoken123", "rating": "9", "body": "Invalid rating test body."})
    print("bad rating POST rows:", Review.query.count(), "(want 0)")

    r = client.post("/product/rust-external-private/review", data={
        "rating": "5", "body": "No csrf token sent."})
    print("no-CSRF POST ->", r.status_code, "(want 400)")

    Review.query.delete()
    Key.query.filter_by(key_value="TEST-KEY-REVIEW-1").delete()
    db.session.commit()
    print("cleanup done; reviews:", Review.query.count())
