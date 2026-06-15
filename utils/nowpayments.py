import hmac
import hashlib
import requests
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api.nowpayments.io/v2"
TIMEOUT = 30


class NOWPayments:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key
        self.base = base_url or BASE_URL

    def _headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def create_invoice(self, amount, currency="USD", order_id=None, description=None,
                       success_url=None, cancel_url=None, ipn_callback_url=None):
        payload = {
            "price_amount": amount,
            "price_currency": currency,
            "order_id": order_id,
        }
        if description:
            payload["order_description"] = description
        if success_url:
            payload["success_url"] = success_url
        if cancel_url:
            payload["cancel_url"] = cancel_url
        if ipn_callback_url:
            payload["ipn_callback_url"] = ipn_callback_url

        url = f"{self.base}/invoice"
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()


def verify_ipn(data, ipn_secret):
    try:
        received = data.pop("hmac", "")
        sorted_keys = sorted(data.keys())
        values = ""
        for k in sorted_keys:
            if isinstance(data[k], (int, float)):
                values += str(data[k])
            else:
                values += str(data[k])
        expected = hmac.new(
            ipn_secret.encode() if isinstance(ipn_secret, str) else ipn_secret,
            values.encode(),
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(received, expected)
    except Exception as e:
        logger.warning("NOWPayments IPN verification error: %s", e)
        return False
