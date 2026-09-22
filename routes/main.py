from pathlib import Path
import io
import json
import time
import threading
import logging
from datetime import datetime

from flask import Blueprint, render_template, abort, current_app, Response, redirect, request, url_for, flash
from flask_login import login_required, current_user
from models import db, Product, Key, PricingTier, User, Order, Review
from config import get_loader_config, get_discord_config

main_bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


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


def _get_product_features_from_db(product):
    items = []
    if product and product.features_text:
        items = [line.strip() for line in product.features_text.splitlines() if line.strip()]
    if not items:
        items = [
            "Core external toolkit with visual overlays",
            "Regular update maintenance included",
            "Private Discord support channel",
            "Configure features in Admin -> Tiers -> Product Content",
        ]
    return {
        "label": product.name if product else "Features",
        "items": items,
    }


@main_bp.route("/cheat-image/<slug>")
def cheat_image(slug):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        abort(404)

    if product.image_url:
        # Only redirect when the target actually exists: a set-but-broken
        # image_url would otherwise 404 at the redirect target and defeat
        # the card's onerror fallback to this placeholder. External URLs
        # cannot be verified locally, so they keep the plain redirect.
        from pathlib import Path as _Path
        if product.image_url.startswith("/static/"):
            static_file = _Path(current_app.root_path) / "static" / product.image_url[len("/static/"):]
            if not static_file.is_file():
                # Missing static file -> fall through to the placeholder.
                pass
            else:
                return redirect(product.image_url)
        else:
            return redirect(product.image_url)

    from PIL import Image, ImageDraw, ImageFont

    is_private = product.visibility == "private"
    accent = (30, 58, 95) if is_private else (212, 212, 216)
    accent_dark = (21, 42, 68) if is_private else (100, 100, 110)

    width, height = 600, 340
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(9 + ratio * 10)
        g = int(11 + ratio * 18)
        b = int(27 + ratio * 22)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    for i in range(3):
        cx = int(width * (0.25 + i * 0.25))
        cy = int(height * (0.4 + i * 0.15))
        r_max = int(width * 0.42)
        for rad in range(r_max, 0, -1):
            alpha = int(max(0, 18 - (rad / r_max) * 18))
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(accent[0], accent[1], accent[2], alpha))

    for i in range(40):
        x0 = i * (width // 40)
        x1 = x0 + (width // 80)
        draw.rectangle([x0, 0, x1, height], fill=(accent[0], accent[1], accent[2], 3))

    label = "BEAZT PRIVATE" if is_private else "LICENSE"
    try:
        font_label = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_label = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font_label)
    lw = bbox[2] - bbox[0]
    label_x = (width - lw) // 2
    draw.rectangle([label_x - 14, 132, label_x + lw + 14, 156], fill=(accent[0], accent[1], accent[2], 40))
    draw.text((label_x, 134), label, fill=accent, font=font_label)

    name = product.name
    try:
        font_name = ImageFont.truetype("impact.ttf", 36)
    except Exception:
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 34)
        except Exception:
            font_name = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), name, font=font_name)
    tw = bbox[2] - bbox[0]
    if tw > width - 40:
        try:
            font_name = ImageFont.truetype("impact.ttf", 28)
        except Exception:
            font_name = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), name, font=font_name)
        tw = bbox[2] - bbox[0]
    tx = (width - tw) // 2
    draw.text((tx + 2, 162), name, fill=(0, 0, 0, 120), font=font_name)
    draw.text((tx, 160), name, fill=(255, 255, 255), font=font_name)

    try:
        font_sub = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font_sub = ImageFont.load_default()
    sub_text = "Private Build" if is_private else "Instant Key Delivery"
    bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = bbox[2] - bbox[0]
    draw.text(((width - sw) // 2, 215), sub_text, fill=(180, 180, 200), font=font_sub)

    try:
        font_tag = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        font_tag = ImageFont.load_default()
    tier_count = PricingTier.query.filter_by(product_id=product.id).count()
    tag_text = f"{tier_count} PLAN(S) AVAILABLE" if tier_count > 0 else "COMING SOON"
    bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w = bbox[2] - bbox[0]
    tag_x = (width - tag_w) // 2
    draw.rectangle([tag_x - 12, 296, tag_x + tag_w + 12, 318], fill=(accent[0], accent[1], accent[2], 30))
    draw.text((tag_x, 298), tag_text, fill=accent, font=font_tag)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png")


# --- ChairFBI live status ----------------------------------------------------
# The ChairFBI API is rate limited to 100 requests/minute per token. Catalogue,
# status, and product pages each render N products, so status must be fetched
# once per TTL window and shared — never once per product per render. A short
# negative cache also stops hammering the API (and stalling renders) when it's
# down or rate limited.
_CHAIRFBI_STATUS_TTL = 45      # seconds: fresh data window
_CHAIRFBI_ERROR_TTL = 20       # seconds: cool-down after a failed fetch
_chairfbi_status_cache = {"cheats": None, "fetched_at": 0.0, "error_until": 0.0}
_chairfbi_status_lock = threading.Lock()


def _fetch_chairfbi_status():
    """Return the live /api/status cheat list, shared via a TTL cache.

    One API call per window serves every product on the site. Returns None
    when the token is unconfigured or when the last fetch failed within the
    cool-down window (callers fall back to admin-set product status).
    """
    from config import get_chairfbi_config
    cfg = get_chairfbi_config()
    if not cfg.get("api_token"):
        return None

    now = time.time()
    with _chairfbi_status_lock:
        if (
            _chairfbi_status_cache["cheats"] is not None
            and now - _chairfbi_status_cache["fetched_at"] < _CHAIRFBI_STATUS_TTL
        ):
            return _chairfbi_status_cache["cheats"]
        if now < _chairfbi_status_cache["error_until"]:
            return None
        try:
            from utils.chairfbi import ChairFBI
            cf = ChairFBI(api_token=cfg["api_token"], base_url=cfg.get("api_base"))
            cheats = cf.get_cheats()
            if not isinstance(cheats, list):
                cheats = []
            _chairfbi_status_cache["cheats"] = cheats
            _chairfbi_status_cache["fetched_at"] = time.time()
            _chairfbi_status_cache["error_until"] = 0.0
            return cheats
        except Exception as exc:  # noqa: BLE001 - storefront must not break on API errors
            logger.warning("ChairFBI status fetch failed: %s", exc)
            _chairfbi_status_cache["error_until"] = time.time() + _CHAIRFBI_ERROR_TTL
            return None


_chairfbi_bases_cache = {"data": None, "fetched_at": 0.0, "error_until": 0.0}


def _fetch_chairfbi_bases():
    """Live /api/status-bases (cheat-base/loader status), TTL-cached.

    Returns a list of {id, name, enabled, status} dicts, or None when the
    integration is unconfigured or unavailable.
    """
    from config import get_chairfbi_config
    cfg = get_chairfbi_config()
    if not cfg.get("api_token"):
        return None

    now = time.time()
    with _chairfbi_status_lock:
        if (
            _chairfbi_bases_cache["data"] is not None
            and now - _chairfbi_bases_cache["fetched_at"] < _CHAIRFBI_STATUS_TTL
        ):
            return _chairfbi_bases_cache["data"]
        if now < _chairfbi_bases_cache["error_until"]:
            return None
        try:
            from utils.chairfbi import ChairFBI
            cf = ChairFBI(api_token=cfg["api_token"], base_url=cfg.get("api_base"))
            bases = cf.get_cheat_bases()
            if not isinstance(bases, list):
                bases = []
            _chairfbi_bases_cache["data"] = bases
            _chairfbi_bases_cache["fetched_at"] = time.time()
            _chairfbi_bases_cache["error_until"] = 0.0
            return bases
        except Exception as exc:  # noqa: BLE001
            logger.warning("ChairFBI base status fetch failed: %s", exc)
            _chairfbi_bases_cache["error_until"] = time.time() + _CHAIRFBI_ERROR_TTL
            return None


def _get_chairfbi_cheat_status(product):
    if not product:
        return None
    # Admin-set status takes priority
    if product.status and product.status not in ("undetected",):
        return product.status
    # Otherwise check the (cached) ChairFBI API status list
    if not product.chairfbi_cheat_id:
        return product.status or "undetected"
    cheats = _fetch_chairfbi_status()
    if cheats:
        for c in cheats:
            cid = str(c.get("id", ""))
            cname = c.get("name", "")
            if cid == product.chairfbi_cheat_id or cname == product.chairfbi_cheat_id:
                return "online" if c.get("active") else "offline"
    return None


def _get_product_gallery(slug, product=None):
    images = []

    if product and product.gallery_images:
        try:
            import json
            vc_images = json.loads(product.gallery_images)
            if isinstance(vc_images, list):
                images.extend(vc_images)
        except (json.JSONDecodeError, TypeError):
            pass

    gallery_dir = Path(current_app.root_path) / "static" / "images" / "products" / slug
    if gallery_dir.exists() and gallery_dir.is_dir():
        allowed = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
        for file_path in sorted(gallery_dir.iterdir()):
            if file_path.suffix.lower() in allowed:
                images.append(f"/static/images/products/{slug}/{file_path.name}")

    if not images and product and product.image_url:
        images.append(product.image_url)
    elif not images and product is None:
        pass

    return images


# --- Catalogue helpers -------------------------------------------------------
# One source of truth: every price, status, and rating below is derived from
# Product/PricingTier/Key/Review rows. Nothing hardcoded, nothing fabricated.

_STATUS_LABELS = {
    "online": "Undetected",
    "maintenance": "Maintenance",
    "updating": "Updating",
}


def _normalize_status(raw_status):
    """Map admin/ChairFBI status values onto the storefront badge taxonomy."""
    s = (raw_status or "").strip().lower()
    if s in ("undetected", "online"):
        return "online"
    if s == "maintenance":
        return "maintenance"
    if s == "offline":
        return "updating"
    return "online"


def _available_pool_count(product):
    """Unassigned pool keys (same definition as the admin panel's pool_count).

    Returns None for chairfbi/license products — their supply is not pool-bound.
    """
    if product.key_source != "pool":
        return None
    return Key.query.filter_by(
        product_id=product.id, user_id=None, is_active=False
    ).count()


def _review_summaries(product_ids):
    """Approved-review aggregates keyed by product_id.

    Products with zero approved reviews are absent from the result — callers
    must treat that as "no rating shown" (never fabricate a score).
    """
    if not product_ids:
        return {}
    reviews = (
        Review.query.filter(
            Review.product_id.in_(product_ids), Review.status == "approved"
        ).all()
    )
    acc = {}
    for r in reviews:
        d = acc.setdefault(r.product_id, {"count": 0, "sum": 0})
        d["count"] += 1
        d["sum"] += r.rating
    return {
        pid: {"count": d["count"], "avg": round(d["sum"] / d["count"], 1)}
        for pid, d in acc.items()
    }


def _catalog_cards(products):
    """Build the storefront card view-model for the given products."""
    summaries = _review_summaries([p.id for p in products])
    cards = []
    for p in products:
        # Cheapest first so the card's "From £X" always reflects the minimum.
        tiers = (
            PricingTier.query.filter_by(product_id=p.id)
            .order_by(PricingTier.price_pence)
            .all()
        )
        status = _normalize_status(_get_chairfbi_cheat_status(p) or p.status)
        pool = _available_pool_count(p)
        durations = sorted({t.duration_days for t in tiers})
        summary = summaries.get(p.id, {})
        cards.append({
            "product": p,
            "slug": p.slug,
            "name": p.name,
            "game": p.display_game,
            "game_slug": p.game_slug,
            "is_private": p.visibility == "private",
            "status": status,
            "status_label": _STATUS_LABELS[status],
            "price_pounds": tiers[0].price_pounds if tiers else None,
            "duration_days": durations[0] if durations else None,
            "tier_count": len(tiers),
            "review_count": summary.get("count", 0),
            "review_avg": summary.get("avg"),
            "out_of_stock": pool == 0 and bool(tiers),
            "updated_at": p.updated_at or p.created_at,
        })
    return cards


def _sort_cards(cards, sort):
    """Sort card view-models. 'featured' = newest first, private pinned top."""
    sort = (sort or "featured").strip()
    if sort == "price-asc":
        cards.sort(key=lambda c: (c["price_pounds"] is None, c["price_pounds"] or 0))
    elif sort == "price-desc":
        cards.sort(key=lambda c: (c["price_pounds"] is None, -(c["price_pounds"] or 0)))
    elif sort == "newest":
        cards.sort(key=lambda c: c["updated_at"] or datetime.min, reverse=True)
    elif sort == "name":
        cards.sort(key=lambda c: c["name"].lower())
    else:
        sort = "featured"
        # Stable sort: private builds first, otherwise newest first (DB order).
        cards.sort(key=lambda c: not c["is_private"])
    return sort


def _group_cards_by_game(cards):
    """Group cards into ordered game sections (first-seen order)."""
    groups = {}
    order = []
    for c in cards:
        key = c["game_slug"] or "other"
        if key not in groups:
            groups[key] = {"slug": key, "name": c["game"], "cards": []}
            order.append(key)
        groups[key]["cards"].append(c)
    return [groups[k] for k in order]


def _user_can_review(product, user_id):
    """Verified buyer = completed order for a tier of this product, or an
    active key assigned to them (covers admin-assigned pool keys)."""
    has_completed_order = (
        Order.query.join(PricingTier, Order.tier_id == PricingTier.id)
        .filter(
            Order.user_id == user_id,
            PricingTier.product_id == product.id,
            Order.status == "completed",
        )
        .first()
    )
    if has_completed_order:
        return True
    return (
        Key.query.filter_by(
            user_id=user_id, product_id=product.id, is_active=True
        ).first()
        is not None
    )


def _apply_catalogue_filters(cards, q, game, status):
    """Filter catalogue cards by free-text query, game slug, and status."""
    q = (q or "").strip().lower()
    game = (game or "").strip().lower()
    status = (status or "").strip().lower()
    out = cards
    if q:
        out = [
            c for c in out
            if q in c["name"].lower() or q in c["game"].lower()
            or (c["product"].description or "").lower().find(q) >= 0
        ]
    if game:
        out = [c for c in out if c["game_slug"] == game]
    if status in ("online", "maintenance", "updating"):
        out = [c for c in out if c["status"] == status]
    return out


@main_bp.route("/")
def index():
    # Newest first: newly added products must be visible in the catalogue
    # immediately after creation (ordering intent from store-section fix).
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    cards = _catalog_cards(all_products)
    sort = _sort_cards(cards, request.args.get("sort"))
    filters = {
        "q": (request.args.get("q") or "").strip(),
        "game": (request.args.get("game") or "").strip().lower(),
        "status": (request.args.get("status") or "").strip().lower(),
    }
    all_games = _group_cards_by_game(cards)
    cards = _apply_catalogue_filters(cards, **filters)
    game_groups = _group_cards_by_game(cards)
    private_cards = [c for c in cards if c["is_private"]]

    # Hero status strip aggregates, computed server-side from live statuses.
    online_count = sum(1 for c in cards if c["status"] == "online")
    last_updated = max(
        (c["updated_at"] for c in cards if c["updated_at"]), default=None
    )

    # Latest approved reviews for the homepage proof section (may be empty —
    # the template shows an honest empty state, never fabricated quotes).
    latest_reviews = (
        Review.query.filter_by(status="approved")
        .order_by(Review.created_at.desc())
        .limit(6)
        .all()
    )

    discord_cfg = get_discord_config()
    return render_template(
        "index.html",
        cards=cards,
        game_groups=game_groups,
        all_games=all_games,
        private_cards=private_cards,
        sort=sort,
        filters=filters,
        catalog_summary={
            "online": online_count,
            "total": len(cards),
            "last_updated": last_updated,
        },
        latest_reviews=latest_reviews,
        discord_public_url=discord_cfg["public_url"],
    )


@main_bp.route("/cheats")
def cheats():
    # Newest first so freshly added products surface at the top of the store.
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    cards = _catalog_cards(all_products)
    sort = _sort_cards(cards, request.args.get("sort"))
    filters = {
        "q": (request.args.get("q") or "").strip(),
        "game": (request.args.get("game") or "").strip().lower(),
        "status": (request.args.get("status") or "").strip().lower(),
    }
    all_games = _group_cards_by_game(cards)
    cards = _apply_catalogue_filters(cards, **filters)
    game_groups = _group_cards_by_game(cards)
    return render_template(
        "cheats.html",
        cards=cards,
        game_groups=game_groups,
        all_games=all_games,
        sort=sort,
        filters=filters,
    )


@main_bp.route("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        abort(404)
    tiers = (
        PricingTier.query
        .filter_by(product_id=product.id)
        .order_by(PricingTier.duration_days)
        .all()
    )
    preselected_id = request.args.get("tier_id", type=int)
    selected_tier = None
    if preselected_id:
        selected_tier = next((t for t in tiers if t.id == preselected_id), None)
    if not selected_tier:
        selected_tier = next((t for t in tiers if t.duration_days == 30), tiers[0] if tiers else None)

    product_features = _get_product_features_from_db(product)
    cheat_status = _get_chairfbi_cheat_status(product)
    gallery_images = _get_product_gallery(product.slug, product=product)

    vc_specs = None
    vc_features = []
    vc_status = None
    vc_system_features = []
    vc_cap_names = {}
    if product.venomcheats_data:
        try:
            vc_data = json.loads(product.venomcheats_data)
            vc_specs = {
                'os': vc_data.get('operatingSystem', ''),
                'cpu': vc_data.get('processor', ''),
                'ac': vc_data.get('antiCheat', ''),
            }
            vc_features = vc_data.get('capabilities', [])
            vc_status = vc_data.get('status', '')
        except (json.JSONDecodeError, TypeError):
            pass

    try:
        from utils.venomcheats import CAPABILITY_NAMES, SYSTEM_FEATURES
        vc_cap_names = CAPABILITY_NAMES
        vc_system_features = SYSTEM_FEATURES
    except ImportError:
        pass

    variants = []
    for t in tiers:
        variants.append({
            "id": t.id,
            "label": t.label,
            "duration_days": t.duration_days,
            "price_pence": t.price_pence,
            "price_pounds": t.price_pounds,
            "billing_type": t.billing_type,
            "subscription_link": t.ivno_subscription_link or "",
        })

    # Verified reviews: approved only, aggregated only when at least one exists.
    reviews = (
        Review.query.filter_by(product_id=product.id, status="approved")
        .order_by(Review.created_at.desc())
        .all()
    )
    review_avg = (
        round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
    )
    can_review = (
        current_user.is_authenticated
        and not Review.query.filter_by(
            user_id=current_user.id, product_id=product.id
        ).first()
        and _user_can_review(product, current_user.id)
    )

    # Other products in the same game, for the "more in <game>" strip.
    related_cards = []
    if product.game:
        same_game = Product.query.filter(
            Product.game == product.game, Product.id != product.id
        ).order_by(Product.created_at.desc()).all()
        related_cards = _catalog_cards(same_game)

    return render_template(
        "product.html",
        product=product,
        tiers=tiers,
        selected_tier=selected_tier,
        gallery_images=gallery_images,
        product_features=product_features,
        cheat_status=cheat_status,
        variants=variants,
        vc_specs=vc_specs,
        vc_features=vc_features,
        vc_status=vc_status,
        vc_cap_names=vc_cap_names,
        vc_system_features=vc_system_features,
        reviews=reviews,
        review_avg=review_avg,
        can_review=can_review,
        related_cards=related_cards,
    )


@main_bp.route("/product/<slug>/review", methods=["POST"])
@login_required
def submit_review(slug):
    """Verified-buyer review submission (moderated before it appears)."""
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        abort(404)
    product_url = url_for("main.product_detail", slug=slug) + "#reviews"
    if not _user_can_review(product, current_user.id):
        flash("Only verified buyers can review this product.", "error")
        return redirect(product_url)
    if Review.query.filter_by(user_id=current_user.id, product_id=product.id).first():
        flash("You have already reviewed this product.", "error")
        return redirect(product_url)

    rating = request.form.get("rating", type=int)
    title = (request.form.get("title") or "").strip()[:128]
    body = (request.form.get("body") or "").strip()
    if not rating or not (1 <= rating <= 5) or len(body) < 10:
        flash("Pick a 1-5 star rating and write at least 10 characters.", "error")
        return redirect(product_url)

    # Attach the fulfilled order that qualified the buyer, if any.
    qualifying_order = (
        Order.query.join(PricingTier, Order.tier_id == PricingTier.id)
        .filter(
            Order.user_id == current_user.id,
            PricingTier.product_id == product.id,
            Order.status == "completed",
        )
        .first()
    )
    review = Review(
        user_id=current_user.id,
        product_id=product.id,
        order_id=qualifying_order.id if qualifying_order else None,
        rating=rating,
        title=title or None,
        body=body,
        status="pending",
    )
    db.session.add(review)
    db.session.commit()
    flash("Thanks! Your review was submitted and appears once approved.", "success")
    return redirect(product_url)


@main_bp.route("/games")
def games_index():
    """Index of all games that have products (crawlable category hub)."""
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    game_groups = _group_cards_by_game(_catalog_cards(all_products))
    games = [
        {
            "slug": g["slug"],
            "name": g["name"],
            "count": len(g["cards"]),
            "online": sum(1 for c in g["cards"] if c["status"] == "online"),
            "price_min": min(
                (c["price_pounds"] for c in g["cards"] if c["price_pounds"] is not None),
                default=None,
            ),
            "card": g["cards"][0] if g["cards"] else None,
        }
        for g in game_groups
    ]
    return render_template("games.html", games=games, game_name=None, cards=[])


@main_bp.route("/games/<game_slug>")
def game_page(game_slug):
    """Per-game landing page: every product for one game, server-rendered."""
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    cards = [
        c for c in _catalog_cards(all_products)
        if c["game_slug"] == game_slug.strip().lower()
    ]
    if not cards:
        abort(404)
    game_name = cards[0]["game"]
    return render_template("games.html", games=None, game_name=game_name, cards=cards)


@main_bp.route("/status")
def status_page():
    """Full live status board: every product, real statuses only."""
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    cards = _catalog_cards(all_products)
    online_count = sum(1 for c in cards if c["status"] == "online")
    last_updated = max(
        (c["updated_at"] for c in cards if c["updated_at"]), default=None
    )
    base_statuses = _fetch_chairfbi_bases()
    return render_template(
        "status.html",
        cards=cards,
        online_count=online_count,
        last_updated=last_updated,
        base_statuses=base_statuses,
    )


@main_bp.route("/sitemap.xml")
def sitemap():
    """XML sitemap: static pages, product pages, and game landing pages."""
    site_url = (current_app.config.get("SITE_URL") or "http://localhost:5000").rstrip("/")
    static_pages = [
        ("/", 1.0, "daily"),
        ("/cheats", 0.9, "daily"),
        ("/games", 0.8, "daily"),
        ("/status", 0.6, "hourly"),
        ("/faq", 0.5, "monthly"),
        ("/feedback", 0.5, "weekly"),
        ("/loader", 0.5, "monthly"),
        ("/terms-of-service", 0.2, "yearly"),
        ("/privacy", 0.2, "yearly"),
    ]
    urls = []
    for path, priority, freq in static_pages:
        urls.append(
            f"  <url><loc>{site_url}{path}</loc><changefreq>{freq}</changefreq>"
            f"<priority>{priority:.1f}</priority></url>"
        )
    products = Product.query.order_by(Product.created_at.desc()).all()
    for p in products:
        lastmod = (p.updated_at or p.created_at or datetime.utcnow()).strftime("%Y-%m-%d")
        urls.append(
            f"  <url><loc>{site_url}{url_for('main.product_detail', slug=p.slug)}</loc>"
            f"<lastmod>{lastmod}</lastmod><changefreq>daily</changefreq>"
            f"<priority>0.9</priority></url>"
        )
    games = sorted({
        p.game_slug for p in products if p.game_slug
    })
    for slug in games:
        urls.append(
            f"  <url><loc>{site_url}{url_for('main.game_page', game_slug=slug)}</loc>"
            f"<changefreq>daily</changefreq><priority>0.7</priority></url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )
    return Response(xml, mimetype="application/xml")


@main_bp.route("/robots.txt")
def robots():
    site_url = (current_app.config.get("SITE_URL") or "http://localhost:5000").rstrip("/")
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /my-keys\n"
        "Disallow: /profile\n"
        "Disallow: /checkout\n"
        f"Sitemap: {site_url}/sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


@main_bp.route("/plan/<int:tier_id>")
def plan_detail(tier_id):
    tier = db.session.get(PricingTier, tier_id)
    if not tier:
        abort(404)
    product = Product.query.filter_by(id=tier.product_id).first()
    if not product:
        abort(404)
    return redirect(url_for("main.product_detail", slug=product.slug, tier_id=tier_id))


@main_bp.route("/loader")
def loader():
    products = Product.query.order_by(Product.created_at.asc()).all()
    loader_cfg = get_loader_config()
    return render_template(
        "loader.html",
        product=None,
        products=products,
        loader_url=loader_cfg["loader_url"],
        loader_public_url=loader_cfg["loader_public_url"],
        loader_private_url=loader_cfg["loader_private_url"],
    )


@main_bp.route("/loader/<slug>")
def loader_product(slug):
    """Product-specific loader guide (VAL-LOADER-002).

    Additive presentation hook: renders the same loader.html template with
    product context (name, status, loader_url, buyer_notes) so each product
    gets correct download instructions and loader URL. The generic /loader
    route above is unchanged.
    """
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        abort(404)
    products = Product.query.order_by(Product.created_at.asc()).all()
    loader_cfg = get_loader_config()
    return render_template(
        "loader.html",
        product=product,
        products=products,
        loader_url=loader_cfg["loader_url"],
        loader_public_url=loader_cfg["loader_public_url"],
        loader_private_url=loader_cfg["loader_private_url"],
    )


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


@main_bp.route("/health/products")
def health_products():
    from models import Product
    products = Product.query.all()
    rows = []
    for p in products:
        rows.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "visibility": p.visibility,
            "key_source": p.key_source,
            "is_private": p.is_private,
            "has_vc": bool(p.venomcheats_slug),
        })
    import os as _os
    return {
        "count": len(rows),
        "products": rows,
        "vercel": _os.environ.get("VERCEL") == "1",
        "db_path": current_app.config.get("SQLALCHEMY_DATABASE_URI", "")[:80],
    }


@main_bp.route("/health/kv")
def health_kv():
    import os as _os
    keys_found = {}
    for k in sorted(_os.environ.keys()):
        kl = k.lower()
        if "kv" in kl or "redis" in kl or "upstash" in kl:
            keys_found[k] = _os.environ[k][:20] + "..."
    return {
        "kv_available": bool(_os.environ.get("KV_REST_API_URL") or _os.environ.get("KV_URL")),
        "kv_keys_found": keys_found,
        "all_env_prefixes": sorted(set(k.split("_")[0] for k in _os.environ.keys())),
    }


@main_bp.route("/my-keys")
@login_required
def my_keys():
    keys = (
        Key.query
        .filter_by(user_id=current_user.id)
        .order_by(Key.created_at.desc())
        .all()
    )
    pending_orders = (
        Order.query
        .filter_by(user_id=current_user.id, status="awaiting_keys")
        .order_by(Order.created_at.desc())
        .all()
    )
    loader = get_loader_config()
    discord_cfg = get_discord_config()
    has_private = any(k.product and k.product.visibility == "private" and k.is_active for k in keys)
    return render_template("keys.html", keys=keys, pending_orders=pending_orders,
        loader_token=loader["loader_token"],
        loader_url=loader["loader_url"],
        loader_public_url=loader["loader_public_url"],
        loader_private_url=loader["loader_private_url"],
        discord_public_url=discord_cfg["public_url"],
        discord_private_url=discord_cfg["private_url"],
        has_private=has_private,
        now=datetime.utcnow())


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if email and email != current_user.email:
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != current_user.id:
                flash("Email already in use.", "error")
                return redirect(url_for("main.profile"))
            current_user.email = email

        if new_password:
            if not current_user.check_password(current_password):
                flash("Current password is incorrect.", "error")
                return redirect(url_for("main.profile"))
            if new_password != confirm_password:
                flash("New passwords do not match.", "error")
                return redirect(url_for("main.profile"))
            if len(new_password) < 6:
                flash("Password must be at least 6 characters.", "error")
                return redirect(url_for("main.profile"))
            current_user.set_password(new_password)

        db.session.commit()
        # Persist the change (notably an admin password change) to the KV
        # backup immediately — restore_users_to_db() re-applies the backup's
        # password_hash for admins on every boot, so without this the change
        # would be reverted until the 120s periodic backup runs (or forever
        # if the app restarts first). Same pattern as routes/auth.py signup.
        try:
            from utils.kv_store import backup_everything
            backup_everything()
        except Exception:
            pass
        flash("Profile updated.", "success")
        return redirect(url_for("main.profile"))

    return render_template("profile.html")
