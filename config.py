import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "instance", "beazt.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SITE_URL = os.getenv("SITE_URL", "http://localhost:5000")
    DISCORD_PUBLIC_URL = os.getenv("DISCORD_PUBLIC_URL", "https://discord.gg/bU4tFA43KK")
    DISCORD_PRIVATE_URL = os.getenv("DISCORD_PRIVATE_URL", "")
    CHAIRFBI_API_TOKEN = os.getenv("CHAIRFBI_API_TOKEN", "")
    CHAIRFBI_API_BASE = os.getenv("CHAIRFBI_API_BASE", "https://access.chairfbi.com")
    LOADER_TOKEN = os.getenv("LOADER_TOKEN", "")
    LOADER_URL = os.getenv("LOADER_URL", "")
    IVNO_API_KEY = os.getenv("IVNO_API_KEY", "iv_live_042bbd72dde8efc2a5c4420f5900a95c")
    IVNO_API_SECRET = os.getenv("IVNO_API_SECRET", "iv_secret_d90978fee4a3d5485fbf749b36f935fb793f34a92b9d0776")
    LOADER_PUBLIC_URL = os.getenv("LOADER_PUBLIC_URL", "")
    LOADER_PRIVATE_URL = os.getenv("LOADER_PRIVATE_URL", "")
    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")
    LICENSE_API_URL = os.getenv("LICENSE_API_URL", "http://panel.projectinfinity.co.za:3845")
    LICENSE_API_TOKEN = os.getenv("LICENSE_API_TOKEN", "26423d5a67ad0f0ec65f27751d12c96cfd8a8ff5a8aa9c7522e8cc4fbb311d7740998388c360cf8311b65be008c021dcf41c207be1aadfaa1ea8d7ab6fb4d88b")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or 587)
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "1") not in ("0", "false", "False", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "BEAZT")


def get_chairfbi_config():
    from models import Setting

    def _lookup(key, default):
        try:
            val = Setting.get(key)
            if val:
                return val
        except Exception:
            pass
        return default

    return {
        "api_token": _lookup("chairfbi_api_token", Config.CHAIRFBI_API_TOKEN),
        "api_base": _lookup("chairfbi_api_base", Config.CHAIRFBI_API_BASE),
    }


def get_loader_config():
    from models import Setting

    def _lookup(key, default):
        try:
            val = Setting.get(key)
            if val:
                return val
        except Exception:
            pass
        return default

    return {
        "loader_token": _lookup("loader_token", Config.LOADER_TOKEN),
        "loader_url": _lookup("loader_url", Config.LOADER_URL),
        "loader_public_url": _lookup("loader_public_url", Config.LOADER_PUBLIC_URL),
        "loader_private_url": _lookup("loader_private_url", Config.LOADER_PRIVATE_URL),
    }


def get_ivno_config():
    from models import Setting

    def _lookup(key, default):
        try:
            val = Setting.get(key)
            if val:
                return val
        except Exception:
            pass
        return default

    return {
        "api_key": _lookup("ivno_api_key", Config.IVNO_API_KEY),
        "api_secret": _lookup("ivno_api_secret", Config.IVNO_API_SECRET),
    }


def get_discord_config():
    from models import Setting

    def _lookup(key, default):
        try:
            val = Setting.get(key)
            if val:
                return val
        except Exception:
            pass
        return default

    return {
        "public_url": _lookup("discord_public_url", Config.DISCORD_PUBLIC_URL),
        "private_url": _lookup("discord_private_url", Config.DISCORD_PRIVATE_URL),
    }


def get_license_api_config():
    """License API (Project Infinity / CatNip panel) credentials.

    Mirrors the other integration helpers: Settings take precedence over the
    Config env-var defaults, so the token / URL / auth scheme can be updated
    from the admin Settings page without a redeploy.
    """
    from models import Setting

    def _lookup(key, default):
        try:
            val = Setting.get(key)
            if val:
                return val
        except Exception:
            pass
        return default

    scheme = _lookup("license_api_auth_scheme", "raw").strip().lower()
    if scheme not in ("bearer", "raw"):
        scheme = "raw"
    return {
        "api_token": _lookup("license_api_token", Config.LICENSE_API_TOKEN),
        "api_url": _lookup("license_api_url", Config.LICENSE_API_URL),
        "auth_scheme": scheme,
    }


def get_mailer_config():
    """SMTP credentials for the transactional mailer.

    Settings take precedence over Config env defaults so SMTP can be updated
    from the admin Settings page without a redeploy.
    """
    from models import Setting

    def _lookup(key, default):
        try:
            val = Setting.get(key)
            if val:
                return val
        except Exception:
            pass
        return default

    use_tls_val = _lookup("smtp_use_tls", "1" if Config.SMTP_USE_TLS else "0")
    use_tls = str(use_tls_val).strip().lower() in ("1", "true", "yes", "on")
    return {
        "smtp_host": _lookup("smtp_host", Config.SMTP_HOST),
        "smtp_port": _lookup("smtp_port", str(Config.SMTP_PORT)),
        "smtp_user": _lookup("smtp_user", Config.SMTP_USER),
        "smtp_pass": _lookup("smtp_pass", Config.SMTP_PASS),
        "use_tls": use_tls,
        "from_email": _lookup("smtp_from_email", Config.SMTP_FROM_EMAIL),
        "from_name": _lookup("smtp_from_name", Config.SMTP_FROM_NAME),
    }
