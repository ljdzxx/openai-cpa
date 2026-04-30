import random
import re
import string
from html import unescape
from typing import Any, Dict, List, Optional

from curl_cffi import requests

from utils import config as cfg


class MoemailService:
    def __init__(
        self,
        api_url: str,
        api_key: str,
        domain: str = "",
        proxies: Any = None,
        timeout: int = 15,
    ):
        self.api_url = self._normalize_api_url(api_url)
        self.api_key = str(api_key or "").strip()
        self.domain = str(domain or "").strip()
        self.timeout = timeout
        self.session = requests.Session(impersonate="chrome120")
        if proxies:
            self.session.proxies = proxies if isinstance(proxies, dict) else {"http": proxies, "https": proxies}

    @staticmethod
    def _normalize_api_url(api_url: str) -> str:
        value = str(api_url or "").strip().rstrip("/")
        if value.endswith("/api"):
            value = value[:-4]
        return value

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        if not self.api_url:
            raise ValueError("Moemail API 地址未配置")
        if not self.api_key:
            raise ValueError("Moemail API 密钥未配置")

        url = f"{self.api_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers.update(self._headers())
        try:
            if method == "GET":
                resp = self.session.get(url, headers=headers, timeout=self.timeout, **kwargs)
            elif method == "POST":
                resp = self.session.post(url, headers=headers, timeout=self.timeout, **kwargs)
            elif method == "DELETE":
                resp = self.session.delete(url, headers=headers, timeout=self.timeout, **kwargs)
            else:
                raise ValueError(f"unsupported method: {method}")
        except Exception as exc:
            raise RuntimeError(f"Moemail API 请求异常: {exc}") from exc

        if resp.status_code >= 400:
            raise RuntimeError(f"Moemail API 请求失败 HTTP {resp.status_code}: {resp.text[:300]}")

        try:
            data = resp.json()
        except Exception:
            data = {}
        return data if isinstance(data, dict) else {}

    def get_config(self) -> Dict[str, Any]:
        return self._request("GET", "/api/config")

    def _resolve_domain(self) -> str:
        if self.domain:
            return self.domain
        try:
            config = self.get_config()
            raw_domains = str(config.get("emailDomains") or "").strip()
            domains = [d.strip() for d in raw_domains.split(",") if d.strip()]
            if domains:
                return domains[0]
        except Exception as exc:
            print(f"[{cfg.ts()}] [WARNING] Moemail 获取域名配置失败: {exc}")
        return ""

    def create_email(self, name: Optional[str] = None) -> tuple:
        domain = self._resolve_domain()
        if not domain:
            print(f"[{cfg.ts()}] [ERROR] Moemail 邮箱域名未配置，且 /api/config 未返回 emailDomains")
            return None, None

        local_part = str(name or "").strip()
        if not local_part:
            local_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))

        payload = {
            "name": local_part,
            "expiryTime": 3600000,
            "domain": domain,
        }
        try:
            data = self._request("POST", "/api/emails/generate", json=payload)
            email = str(data.get("email") or "").strip()
            email_id = str(data.get("id") or "").strip()
            if email and email_id:
                return email, email_id
            print(f"[{cfg.ts()}] [ERROR] Moemail 创建邮箱返回不完整: {data}")
        except Exception as exc:
            print(f"[{cfg.ts()}] [ERROR] Moemail 创建邮箱失败: {exc}")
        return None, None

    def get_messages(self, email_id: str) -> List[Dict[str, Any]]:
        if not email_id:
            return []
        try:
            data = self._request("GET", f"/api/emails/{email_id}")
            messages = data.get("messages") or []
            return messages if isinstance(messages, list) else []
        except Exception as exc:
            print(f"[{cfg.ts()}] [WARNING] Moemail 获取邮件列表失败: {exc}")
            return []

    def get_message_detail(self, email_id: str, message_id: str) -> Dict[str, Any]:
        if not email_id or not message_id:
            return {}
        try:
            data = self._request("GET", f"/api/emails/{email_id}/{message_id}")
            message = data.get("message") or {}
            return message if isinstance(message, dict) else {}
        except Exception as exc:
            print(f"[{cfg.ts()}] [WARNING] Moemail 获取邮件详情失败: {exc}")
            return {}

    @staticmethod
    def message_text(message: Dict[str, Any]) -> str:
        content = "\n".join(
            str(message.get(key) or "")
            for key in ("from_address", "from", "subject", "content", "text", "body", "html")
        )
        return unescape(re.sub(r"<[^>]+>", " ", content))
