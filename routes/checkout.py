import stripe
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, jsonify, current_app, url_for
from flask_login import current_user, login_required
from models import db, PricingTier, Order, Key
from config import get_stripe_config, get_chairfbi_config

checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/create-session", methods=["POST"])
@login_required
def create_session():
    tier_id = request.form.get("tier_id")
    if not tier_id:
        return jsonify({"error": "No tier selected"}), 400

    tier = db.session.get(PricingTier, int(tier_id))
    if not tier:
        return jsonify({"error": "Invalid tier"}), 400

    cfg = get_stripe_config()
    stripe.api_key = cfg["secret_key"]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            customer_email=current_user.email,
            client_reference_id=str(current_user.id),
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"BeaZt Cheats - {tier.product.name} ({tier.label})",
                        "description": f"{tier.duration_days} day(s) access",
                    },
                    "unit_amount": tier.price_pence,
                },
                "quantity": 1,
            }],
            metadata={
                "user_id": str(current_user.id),
                "tier_id": str(tier.id),
                "duration_days": str(tier.duration_days),
                "product_id": str(tier.product_id),
                "product_slug": tier.product.slug,
            },
            success_url=url_for("main.my_keys", _external=True),
            cancel_url=url_for("main.product_detail", slug=tier.product.slug, _external=True),
        )

        order = Order(
            user_id=current_user.id,
            tier_id=tier.id,
            stripe_session_id=session.id,
            status="pending",
        )
        db.session.add(order)
        db.session.commit()

        return redirect(session.url, code=303)
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 500


@checkout_bp.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    cfg = get_stripe_config()
    endpoint_secret = cfg["webhook_secret"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        handle_checkout_completed(session_data)

    return jsonify({"status": "ok"})


def handle_checkout_completed(session_data):
    stripe_session_id = session_data.get("id")
    order = Order.query.filter_by(stripe_session_id=stripe_session_id).first()
    if not order:
        return

    if order.status == "completed":
        return

    order.status = "completed"

    metadata = session_data.get("metadata", {})
    duration_days = int(metadata.get("duration_days", 30))
    product_id = int(metadata.get("product_id", order.tier.product_id if order.tier else 1))
    expires_at = datetime.utcnow() + timedelta(days=duration_days)

    key_value = ""
    chairfbi_key_id = None
    chairfbi_cheat_id = None

    cfg = get_chairfbi_config()
    cheat_id = cfg.get("rust_cheat_id", "")
    api_token = cfg.get("api_token", "")

    if cheat_id and api_token:
        try:
            from utils.chairfbi import ChairFBI

            cf = ChairFBI(api_token=api_token, base_url=cfg.get("api_base"))
            result = cf.create_key(cheat_id=cheat_id, days=duration_days)

            key_value = result.get("license_key") or result.get("key") or ""
            chairfbi_key_id = str(result.get("key_id") or result.get("id") or "")
            chairfbi_cheat_id = cheat_id
        except Exception:
            current_app.logger.exception("ChairFBI key creation failed")

    if not key_value:
        key_value = "BEAZT-" + secrets.token_hex(16).upper()

    key = Key(
        user_id=order.user_id,
        order_id=order.id,
        product_id=product_id,
        key_value=key_value,
        expires_at=expires_at,
        chairfbi_key_id=chairfbi_key_id,
        chairfbi_cheat_id=chairfbi_cheat_id,
    )
    db.session.add(key)
    db.session.commit()
