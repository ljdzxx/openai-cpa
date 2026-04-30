import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

fake_requests_module = types.SimpleNamespace(get=None, post=None, Session=object)
sys.modules.setdefault("curl_cffi", types.SimpleNamespace(requests=fake_requests_module))
sys.modules.setdefault(
    "utils.db_manager",
    types.SimpleNamespace(
        get_sys_kv=lambda *args, **kwargs: None,
        set_sys_kv=lambda *args, **kwargs: None,
    ),
)
sys.modules.setdefault(
    "utils.auth_core",
    types.SimpleNamespace(generate_payload=lambda *args, **kwargs: ""),
)

from utils.integrations.smsbower_sms import (
    _smsbower_wait_for_country_price_limit,
    try_verify_phone_via_smsbower,
)


class _DummySession:
    pass


class SmsBowerCountryLimitTests(unittest.TestCase):
    def test_auto_pick_enabled_still_uses_configured_country(self):
        attempted_countries = []

        def fake_get_number(proxies, *, service_code="", country_id=None):
            attempted_countries.append(int(country_id))
            return "", "", "NO_NUMBERS", ""

        with patch("utils.integrations.smsbower_sms._smsbower_enabled", return_value=True), \
                patch("utils.integrations.smsbower_sms._smsbower_max_tries", return_value=2), \
                patch("utils.integrations.smsbower_sms.smsbower_get_balance", return_value=(9.92, "")), \
                patch("utils.integrations.smsbower_sms._smsbower_resolve_service_code", return_value="dr"), \
                patch("utils.integrations.smsbower_sms._smsbower_resolve_country_id", return_value=16), \
                patch("utils.integrations.smsbower_sms._smsbower_auto_pick_country", return_value=True), \
                patch("utils.integrations.smsbower_sms._smsbower_pick_country_id", return_value=86) as pick_country_mock, \
                patch("utils.integrations.smsbower_sms._smsbower_reuse_enabled", return_value=False), \
                patch("utils.integrations.smsbower_sms._smsbower_get_number", side_effect=fake_get_number), \
                patch("utils.integrations.smsbower_sms._sleep_interruptible", return_value=False):
            with redirect_stdout(io.StringIO()):
                ok, reason = try_verify_phone_via_smsbower(
                    session=_DummySession(),
                    proxies={"http": "http://proxy", "https": "http://proxy"},
                )

        self.assertFalse(ok)
        self.assertEqual("取号失败 NO_NUMBERS", reason)
        self.assertEqual([16, 16], attempted_countries)
        pick_country_mock.assert_not_called()

    def test_country_price_check_retries_until_price_within_limit(self):
        price_rows = [
            [{"country": 16, "cost": 0.12, "count": 3}],
            [{"country": 16, "cost": 0.09, "count": 3}],
            [{"country": 16, "cost": 0.08, "count": 3}],
        ]

        with patch("utils.integrations.smsbower_sms._smsbower_order_max_price", return_value=0.08), \
                patch("utils.integrations.smsbower_sms._smsbower_order_min_price", return_value=0.05), \
                patch("utils.integrations.smsbower_sms._smsbower_price_retry_count", return_value=3), \
                patch("utils.integrations.smsbower_sms._smsbower_price_retry_delay_sec", return_value=0), \
                patch("utils.integrations.smsbower_sms._smsbower_prices_by_service", side_effect=price_rows) as prices_mock, \
                patch("utils.integrations.smsbower_sms._sleep_interruptible", return_value=False) as sleep_mock:
            with redirect_stdout(io.StringIO()):
                ok, reason = _smsbower_wait_for_country_price_limit(
                    proxies=None,
                    service_code="dr",
                    country_id=16,
                )

        self.assertTrue(ok)
        self.assertEqual("", reason)
        self.assertEqual(3, prices_mock.call_count)
        self.assertEqual(2, sleep_mock.call_count)

    def test_country_price_check_gives_up_after_retry_limit(self):
        with patch("utils.integrations.smsbower_sms._smsbower_order_max_price", return_value=0.08), \
                patch("utils.integrations.smsbower_sms._smsbower_order_min_price", return_value=0.05), \
                patch("utils.integrations.smsbower_sms._smsbower_price_retry_count", return_value=2), \
                patch("utils.integrations.smsbower_sms._smsbower_price_retry_delay_sec", return_value=0), \
                patch("utils.integrations.smsbower_sms._smsbower_prices_by_service",
                      return_value=[{"country": 16, "cost": 0.12, "count": 3}]), \
                patch("utils.integrations.smsbower_sms._sleep_interruptible", return_value=False):
            with redirect_stdout(io.StringIO()):
                ok, reason = _smsbower_wait_for_country_price_limit(
                    proxies=None,
                    service_code="dr",
                    country_id=16,
                )

        self.assertFalse(ok)
        self.assertIn("PRICE_BLOCKED", reason)


if __name__ == "__main__":
    unittest.main()
