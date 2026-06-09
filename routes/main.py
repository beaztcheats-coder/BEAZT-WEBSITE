from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models import Product, Key, PricingTier

main_bp = Blueprint("main", __name__)


def get_product_features(slug):
    feature_sets = {
        "rust-external-private": {
            "label": "Rust External - BeaZt Legit",
            "items": [
                "Legit ESP suite",
                "Debug camera",
                "Player and resource overlays",
                "Distance and visibility tools",
                "Legit-focused presets",
                "Private build updates",
                "Discord setup support",
            ],
        },
    }
    default_set = {
        "label": "Game Access",
        "items": [
            "Core external toolkit",
            "Visualization modules",
            "Update maintenance",
            "Private support channel",
        ],
    }
    return feature_sets.get(slug, default_set)


@main_bp.route("/")
def index():
    product = Product.query.filter_by(slug="rust-external-private").first()
    tiers = []
    product_features = {"label": "Game Access", "items": []}
    if product:
        tiers = (
            PricingTier.query
            .filter_by(product_id=product.id)
            .order_by(PricingTier.duration_days)
            .all()
        )
        product_features = get_product_features(product.slug)
    return render_template("index.html", product=product, tiers=tiers, product_features=product_features)


@main_bp.route("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        abort(404)
    product_features = get_product_features(product.slug)
    tiers = (
        PricingTier.query
        .filter_by(product_id=product.id)
        .order_by(PricingTier.duration_days)
        .all()
    )
    return render_template("product.html", product=product, tiers=tiers, product_features=product_features)


@main_bp.route("/feedback")
def feedback():
    return render_template("feedback.html")


@main_bp.route("/terms-of-service")
def terms():
    return render_template("terms.html")


@main_bp.route("/faq")
def faq():
    return render_template("faq.html")


@main_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@main_bp.route("/my-keys")
@login_required
def my_keys():
    keys = (
        Key.query
        .filter_by(user_id=current_user.id)
        .order_by(Key.created_at.desc())
        .all()
    )
    return render_template("keys.html", keys=keys)
