import logging
import requests

logger = logging.getLogger(__name__)


class LicenseAPI:
    BASE = "https://panel.projectinfinity.co.za"
    TIMEOUT = 15

    def __init__(self, api_token=None, base_url=None):
        self.token = api_token
        self.base = base_url or self.BASE
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method, path, **kwargs):
        url = f"{self.base.rstrip('/')}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.TIMEOUT)
        kwargs.setdefault("headers", self.headers)
        resp = requests.request(method, url, **kwargs)
        return resp

    def get_apps(self):
        resp = self._request("GET", "/backend/dashboard/api/v1/apps")
        resp.raise_for_status()
        return resp.json()

    def get_licenses(self, app_id):
        resp = self._request("GET", f"/backend/dashboard/api/v1/apps/{app_id}/licenses")
        resp.raise_for_status()
        return resp.json()

    def create_keys(self, app_id, duration_days, quantity=1):
        path = f"/backend/dashboard/api/v1/apps/{app_id}/licenses"
        body = {"duration": str(duration_days), "quantity": str(quantity)}
        resp = self._request("POST", path, json=body)
        if resp.status_code >= 400:
            logger.error("License API error %s for app %s: %s",
                         resp.status_code, app_id, resp.text[:500])
        resp.raise_for_status()
        data = resp.json()
        # Normalize various response formats into a flat list
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for fld in ("licenses", "data", "keys", "results"):
                if data.get(fld):
                    return data[fld]
            # Single-key response
            for fld in ("key", "license", "license_key"):
                if data.get(fld):
                    return [data]
        return []

    def delete_key(self, app_id, license_key):
        resp = self._request("DELETE", f"/backend/dashboard/api/v1/apps/{app_id}/licenses/{license_key}")
        resp.raise_for_status()
        return resp.json()

    def reset_hwid(self, app_id, license_key):
        resp = self._request("POST", f"/backend/dashboard/api/v1/apps/{app_id}/licenses/{license_key}/reset-hwid")
        resp.raise_for_status()
        return resp.json()
