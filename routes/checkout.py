import secrets
import logging
from datetime import datetime, timedelta

from flask import Blueprint, request, redirect, jsonify, url_for
from flask_login import current_user, login_required
from models import db, PricingTier, Order, Key, Product
from config import get_ivno_config

checkout_bp = Blueprint("checkout", __name__)
logger = logging.getLogger(__name__)


@checkout_bp.route("/create-session", methods=["POST"])
@login_required
def create_session():
    tier_id = request.form.get("tier_id")
    if not tier_id:
        return jsonify({"error": "No tier selected"}), 400

    tier = db.session.get(PricingTier, int(tier_id))
    if not tier:
        return jsonify({"error": "Invalid tier"}), 400

    cfg = get_ivno_config()
    if not cfg["api_key"]:
        return jsonify({"error": "Ivno API key not configured"}), 500

    order = Order(
        user_id=current_user.id,
        tier_id=tier.id,
        status="pending",
    )
    db.session.add(order)
    db.session.flush()

    try:
        from utils.ivno import IvnoPayments
        ivno = IvnoPayments(api_key=cfg["api_key"], api_secret=cfg["api_secret"], base_url=cfg["base_url"])

        domain = request.host
        if domain and ":" in domain:
            domain = domain.split(":")[0]

        result = ivno.create_payment(
            amount=tier.price_pounds,
            currency="GBP",
            order_id=f"BEAZT-{order.id}",
            return_url=url_for("main.my_keys", _external=True),
            email=current_user.email,
            webhook_url=url_for("checkout.ivno_webhook", _external=True),
            domain=domain,
        )

        if not result.get("success") or not result.get("payment_url"):
            msg = result.get("message", "Payment initialization failed")
            logger.error("Ivno payment creation failed: %s", result)
            return jsonify({"error": msg}), 500

        order.stripe_session_id = result.get("payment_url")
        db.session.commit()
        return jsonify({"payment_url": result["payment_url"]})

    except Exception as e:
        err_msg = str(e)
        try:
            import json as _json
            if hasattr(e, "response") and e.response is not None:
                err_msg = _json.loads(e.response.text).get("message", err_msg)
        except Exception:
            pass
        logger.exception("Ivno session creation failed: %s", err_msg)
        return jsonify({"error": err_msg}), 500


@checkout_bp.route("/ivno-webhook", methods=["POST"])
def ivno_webhook():
    data = request.get_json(silent=True) or {}
    event = data.get("event", "")
    status = data.get("status", "")
    order_id_raw = data.get("order_id", "")

    if not order_id_raw or not order_id_raw.startswith("BEAZT-"):
        logger.warning("Ivno webhook: unrecognized order_id %s", order_id_raw)
        return jsonify({"received": True})

    try:
        order_id = int(order_id_raw.replace("BEAZT-", ""))
    except (ValueError, TypeError):
        return jsonify({"received": True})

    order = db.session.get(Order, order_id)
    if not order:
        logger.warning("Ivno webhook: order %s not found", order_id)
        return jsonify({"received": True})

    if event != "payment.updated":
        return jsonify({"received": True})

    if status == "completed" and order.status != "completed":
        from config import get_ivno_config
        cfg_ivno = get_ivno_config()
        if cfg_ivno.get("api_key", "").startswith("iv_test_"):
            logger.info("Test mode — generating test key via Ivno for order %s", order.id)
            handle_fulfillment_test(order)
        else:
            handle_fulfillment(order)
    elif status == "failed":
        order.status = "failed"
        db.session.commit()

    return jsonify({"received": True})


def handle_fulfillment(order):
    tier = order.tier
    if not tier:
        return

    product = tier.product
    product_id = product.id if product else 1
    duration_days = tier.duration_days
    expires_at = datetime.utcnow() + timedelta(days=duration_days)

    pool_key = (
        Key.query
        .filter_by(product_id=product_id, tier_id=tier.id, user_id=None, is_active=False)
        .order_by(Key.created_at.asc())
        .first()
    )
    if pool_key:
        pool_key.user_id = order.user_id
        pool_key.order_id = order.id
        pool_key.expires_at = expires_at
        pool_key.assigned_at = datetime.utcnow()
        pool_key.is_active = True
        order.status = "completed"
        db.session.commit()
        try:
            from utils.kv_store import backup_everything
            backup_everything()
        except Exception:
            pass
        return

    if product and product.key_source == "pool":
        order.status = "awaiting_keys"
        db.session.commit()
        try:
            from utils.kv_store import backup_everything
            backup_everything()
        except Exception:
            pass
        return

    from config import get_chairfbi_config
    cfg = get_chairfbi_config()
    api_token = cfg.get("api_token", "")
    cheat_id = product.chairfbi_cheat_id if product else ""

    key_value = ""
    chairfbi_key_id = None
    chairfbi_cheat_id = None

    if cheat_id and api_token:
        try:
            from utils.chairfbi import ChairFBI
            cf = ChairFBI(api_token=api_token, base_url=cfg.get("api_base"))
            result = cf.create_key(cheat_id=cheat_id, days=duration_days)
            keys = result.get("keys", [])
            key_value = keys[0] if keys else ""
            chairfbi_key_id = key_value
            chairfbi_cheat_id = cheat_id
        except Exception:
            logger.exception("ChairFBI key creation failed for order %s", order.id)

    if not key_value:
        key_value = "BEAZT-" + secrets.token_hex(16).upper()

    order.status = "completed"
    key = Key(
        user_id=order.user_id,
        order_id=order.id,
        product_id=product_id,
        tier_id=tier.id,
        key_value=key_value,
        expires_at=expires_at,
        chairfbi_key_id=chairfbi_key_id,
        chairfbi_cheat_id=chairfbi_cheat_id,
    )
    db.session.add(key)
    db.session.commit()
    try:
        from utils.kv_store import backup_everything
        backup_everything()
    except Exception:
        pass


def handle_fulfillment_test(order):
    tier = order.tier
    if not tier:
        return

    product = tier.product
    product_id = product.id if product else 1
    duration_days = tier.duration_days
    expires_at = datetime.utcnow() + timedelta(days=duration_days)

    pool_key = (
        Key.query
        .filter_by(product_id=product_id, tier_id=tier.id, user_id=None, is_active=False)
        .order_by(Key.created_at.asc())
        .first()
    )
    if pool_key:
        pool_key.user_id = order.user_id
        pool_key.order_id = order.id
        pool_key.expires_at = expires_at
        pool_key.assigned_at = datetime.utcnow()
        pool_key.is_active = True
        order.status = "completed"
        db.session.commit()
        return

    key_value = "BEAZT-TEST-" + secrets.token_hex(12).upper()
    order.status = "completed"
    key = Key(
        user_id=order.user_id,
        order_id=order.id,
        product_id=product_id,
        tier_id=tier.id,
        key_value=key_value,
        expires_at=expires_at,
    )
    db.session.add(key)
    db.session.commit()
    try:
        from utils.kv_store import backup_everything
        backup_everything()
    except Exception:
        pass


@checkout_bp.route("/payfast", methods=["POST"])
@login_required
def payfast_session():
    tier_id = request.form.get("tier_id")
    if not tier_id:
        return jsonify({"error": "No tier selected"}), 400

    tier = db.session.get(PricingTier, int(tier_id))
    if not tier:
        return jsonify({"error": "Invalid tier"}), 400

    from config import get_payfast_config
    cfg = get_payfast_config()
    if not cfg["merchant_id"] or not cfg["merchant_key"]:
        return jsonify({"error": "PayFast not configured"}), 500

    order = Order(
        user_id=current_user.id,
        tier_id=tier.id,
        status="pending",
    )
    db.session.add(order)
    db.session.flush()

    try:
        from utils.payfast import gbp_to_zar, build_payment_form

        amount_zar = gbp_to_zar(tier.price_pounds)
        item_name = f"{tier.product.name} ({tier.label})"[:100]
        order_ref = f"BEAZT-PF-{order.id}"

        result = build_payment_form(
            amount_zar=amount_zar,
            item_name=item_name,
            order_id=order_ref,
            return_url=url_for("main.my_keys", _external=True),
            cancel_url=url_for("main.cheats", _external=True),
            notify_url=url_for("checkout.payfast_itn", _external=True),
            merchant_id=cfg["merchant_id"],
            merchant_key=cfg["merchant_key"],
            passphrase=cfg["passphrase"],
            email=current_user.email,
        )

        return jsonify(result)
    except Exception as e:
        logger.exception("PayFast session creation failed")
        return jsonify({"error": str(e)}), 500


@checkout_bp.route("/payfast-itn", methods=["POST"])
def payfast_itn():
    from utils.payfast import validate_itn
    valid, msg = validate_itn(request.form)
    if not valid:
        logger.warning("PayFast ITN validation failed: %s", msg)
        return "INVALID"

    pf_payment_id = request.form.get("pf_payment_id", "")
    order_ref = request.form.get("m_payment_id", "")
    payment_status = request.form.get("payment_status", "")

    if not order_ref or not order_ref.startswith("BEAZT-PF-"):
        logger.warning("PayFast ITN: unrecognized order %s", order_ref)
        return "OK"

    try:
        order_id = int(order_ref.replace("BEAZT-PF-", ""))
    except (ValueError, TypeError):
        return "OK"

    order = db.session.get(Order, order_id)
    if not order:
        logger.warning("PayFast ITN: order %s not found", order_id)
        return "OK"

    if payment_status == "COMPLETE" and order.status != "completed":
        handle_fulfillment(order)

    return "OK"
