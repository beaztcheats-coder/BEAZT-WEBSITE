"""ChairFBI integration validation (mocked — no real API calls).

Verifies:
1. Client methods build correct requests (paths, payloads) against a fake session.
2. 429 handling raises ChairFBIRateLimitError with availableIn, and does NOT retry.
3. Status cache: one API call per TTL window across many products/pages.
4. /status page renders with base statuses from /api/status-bases.
5. Admin delete route exists and is registered.
6. All public pages render 200.
"""
import sys
from unittest import mock

sys.path.insert(0, ".")

from app import app  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# 1) Client request construction (mocked requests.request)
# ---------------------------------------------------------------------------
from utils.chairfbi import ChairFBI, ChairFBIRateLimitError  # noqa: E402


class FakeResp:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = str(self._payload)

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"{self.status_code} error")


calls = []


def fake_request(method, url, **kwargs):
    calls.append((method, url, kwargs))
    return FakeResp(200, [])


with mock.patch("utils.chairfbi.requests.request", side_effect=fake_request):
    cf = ChairFBI(api_token="tok", base_url="https://access.chairfbi.com")

    cf.get_cheats()
    check("get_cheats hits /api/status", calls[-1][1].endswith("/api/status") and calls[-1][0] == "GET")
    check("auth header sent", calls[-1][2]["headers"]["Authorization"] == "Bearer tok")

    cf.get_cheat_bases()
    check("get_cheat_bases hits /api/status-bases", calls[-1][1].endswith("/api/status-bases"))

    cf.update_cheats([1, 2], active=False)
    m, u, kw = calls[-1]
    check("update_cheats PUT /api/cheats", m == "PUT" and u.endswith("/api/cheats"))
    check("update_cheats payload", kw["json"] == {"cheats": [1, 2], "active": False})

    cf.delete_keys(["KEY_1"])
    m, u, kw = calls[-1]
    check("delete_keys POST /api/keys-delete", m == "POST" and u.endswith("/api/keys-delete"))
    check("delete_keys payload", kw["json"] == {"keys": ["KEY_1"]})

    cf.request_key_deletion(["KEY_1"], "issue + proof")
    m, u, kw = calls[-1]
    check("request_key_deletion POST /api/keys-delete-request",
          m == "POST" and u.endswith("/api/keys-delete-request"))
    check("request_key_deletion payload",
          kw["json"] == {"keys": ["KEY_1"], "reason": "issue + proof"})

    cf.get_key_deletion_request("KEY_1")
    check("get_key_deletion_request path", calls[-1][1].endswith("/api/key-deletion-request/KEY_1"))

    cf.list_passes(page=2, per_page=10)
    m, u, kw = calls[-1]
    check("list_passes GET /api/passes", m == "GET" and u.endswith("/api/passes"))
    check("list_passes params", kw["params"] == {"page": 2, "per_page": 10})

    cf.create_pass("My Pass")
    m, u, kw = calls[-1]
    check("create_pass POST /api/passes", m == "POST" and kw["json"] == {"name": "My Pass"})

    cf.update_pass(5, name="Renamed", active=True)
    check("update_pass payload", calls[-1][2]["json"] == {"pass": 5, "name": "Renamed", "active": True})

    cf.delete_pass(5)
    m, u, kw = calls[-1]
    check("delete_pass DELETE /api/passes", m == "DELETE" and kw["json"] == {"pass": 5})

    cf.update_pass_cheats(5, [1, 2, 3])
    check("update_pass_cheats payload", calls[-1][2]["json"] == {"pass": 5, "cheats": [1, 2, 3]})

    cf.create_pass_key(3, amount=2, days=15)
    check("create_pass_key payload", calls[-1][2]["json"] == {"pass": 3, "amount": 2, "days": 15})

    try:
        cf.create_pass_key(3, days=10)
        check("create_pass_key rejects invalid days", False)
    except ValueError:
        check("create_pass_key rejects invalid days", True)

    cf.update_pass_keys(["PASSKEY_1"], hwid=True)
    check("update_pass_keys PUT /api/pass-keys",
          calls[-1][0] == "PUT" and calls[-1][2]["json"] == {"keys": ["PASSKEY_1"], "hwid": True})

    cf.delete_pass_keys(["PASSKEY_1"])
    check("delete_pass_keys POST /api/pass-keys-delete",
          calls[-1][0] == "POST" and calls[-1][1].endswith("/api/pass-keys-delete"))

# ---------------------------------------------------------------------------
# 2) 429 handling — raises once, no retries
# ---------------------------------------------------------------------------
rate_limit_calls = []


def rate_limited_request(method, url, **kwargs):
    rate_limit_calls.append(url)
    return FakeResp(429, {"error": True, "code": "rate_limit_exceeded",
                          "message": "Too many requests", "availableIn": 45})


with mock.patch("utils.chairfbi.requests.request", side_effect=rate_limited_request):
    cf2 = ChairFBI(api_token="tok")
    try:
        cf2.get_cheats()
        check("429 raises ChairFBIRateLimitError", False)
    except ChairFBIRateLimitError as e:
        check("429 raises ChairFBIRateLimitError", True)
        check("429 availableIn surfaced", e.available_in == 45, f"got {e.available_in}")
    check("429 not retried (single call)", len(rate_limit_calls) == 1,
          f"got {len(rate_limit_calls)} calls")

# ---------------------------------------------------------------------------
# 3) Status cache — one API call per TTL window across many renders
# ---------------------------------------------------------------------------
import time as _time  # noqa: E402
import routes.main as main_mod  # noqa: E402

# Reset cache state
main_mod._chairfbi_status_cache.update({"cheats": None, "fetched_at": 0.0, "error_until": 0.0})

fetch_calls = []


def fake_get_cheats(self):
    fetch_calls.append(1)
    return [{"id": 7, "name": "Rust External", "active": True, "price_type": "days"}]


with mock.patch("utils.chairfbi.ChairFBI.get_cheats", new=fake_get_cheats), \
     mock.patch("routes.main.get_chairfbi_config" if hasattr(main_mod, "get_chairfbi_config") else "config.get_chairfbi_config",
                return_value={"api_token": "tok", "api_base": None}):
    # config import is lazy inside the function; patch at source module
    import config as config_mod
    with mock.patch.object(config_mod, "get_chairfbi_config",
                           return_value={"api_token": "tok", "api_base": None}):
        status1 = main_mod._get_chairfbi_cheat_status(
            type("P", (), {"status": None, "chairfbi_cheat_id": "7"})())
        status2 = main_mod._get_chairfbi_cheat_status(
            type("P", (), {"status": None, "chairfbi_cheat_id": "Rust External"})())
        status3 = main_mod._get_chairfbi_cheat_status(
            type("P", (), {"status": None, "chairfbi_cheat_id": "999"})())
        # Simulate another render within the TTL window
        status4 = main_mod._get_chairfbi_cheat_status(
            type("P", (), {"status": None, "chairfbi_cheat_id": "7"})())

check("live status online for active cheat", status1 == "online", f"got {status1}")
check("status match by name", status2 == "online", f"got {status2}")
check("unknown cheat falls back to None", status3 is None, f"got {status3}")
check("cached within TTL", status4 == "online")
check("single API call across renders", len(fetch_calls) == 1, f"got {len(fetch_calls)}")

# Admin override still wins over live status
override = main_mod._get_chairfbi_cheat_status(
    type("P", (), {"status": "maintenance", "chairfbi_cheat_id": "7"})())
check("admin status override priority", override == "maintenance")

# Cache reset for later page tests
main_mod._chairfbi_status_cache.update({"cheats": None, "fetched_at": 0.0, "error_until": 0.0})
main_mod._chairfbi_bases_cache.update({"data": None, "fetched_at": 0.0, "error_until": 0.0})

# ---------------------------------------------------------------------------
# 4) Error cool-down: after a failure, subsequent calls within cool-down
#    do not re-hit the API
# ---------------------------------------------------------------------------
fail_calls = []


def failing_get_cheats(self):
    fail_calls.append(1)
    raise RuntimeError("boom")


with mock.patch.object(config_mod, "get_chairfbi_config",
                       return_value={"api_token": "tok", "api_base": None}), \
     mock.patch("utils.chairfbi.ChairFBI.get_cheats", new=failing_get_cheats):
    main_mod._fetch_chairfbi_status()
    main_mod._fetch_chairfbi_status()
    main_mod._fetch_chairfbi_status()

check("error cool-down prevents hammering", len(fail_calls) == 1, f"got {len(fail_calls)}")

# Restore clean cache
main_mod._chairfbi_status_cache.update({"cheats": None, "fetched_at": 0.0, "error_until": 0.0})
main_mod._chairfbi_bases_cache.update({"data": None, "fetched_at": 0.0, "error_until": 0.0})

# ---------------------------------------------------------------------------
# 5) Page rendering through the test client
# ---------------------------------------------------------------------------
with mock.patch.object(config_mod, "get_chairfbi_config",
                       return_value={"api_token": "tok", "api_base": None}), \
     mock.patch("utils.chairfbi.ChairFBI.get_cheats",
                new=lambda self: [{"id": 7, "name": "Rust External", "active": True}]), \
     mock.patch("utils.chairfbi.ChairFBI.get_cheat_bases",
                new=lambda self: [{"id": 1, "name": "Rust Base", "enabled": True, "status": True}]):
    client = app.test_client()
    for path in ("/", "/cheats", "/status", "/games", "/sitemap.xml", "/robots.txt",
                 "/product/rust-external-private", "/health/products"):
        resp = client.get(path)
        check(f"GET {path} -> 200", resp.status_code == 200, f"got {resp.status_code}")

    status_html = client.get("/status").get_data(as_text=True)
    check("/status shows base statuses section", "Cheat base status" in status_html)
    check("/status shows live base name", "Rust Base" in status_html)
    check("/status shows operational pill", "Operational" in status_html)

# Admin delete route registered
rules = {r.rule for r in app.url_map.iter_rules()}
check("admin delete route registered", "/admin/chairfbi/delete/<int:key_id>" in rules)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
