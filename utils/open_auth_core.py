import base64
import json
import time
from typing import Any, Dict, List, Optional, Tuple

from curl_cffi import requests

from utils import config as cfg
from utils.auth_pipeline.http_utils import _ssl_verify
from utils.email_providers.mail_service import mask_email


TEAM_API_BASE = "https://chatgpt.com/backend-api"
INVITE_RETRY_DELAYS = (30, 60)


def email_jwt(token: str) -> Dict[str, Any]:
    token = str(token or "").strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        return {}

    parts = token.split(".")
    candidates = [parts[1]] if len(parts) >= 2 else parts
    for raw in candidates:
        raw = raw.strip()
        if not raw:
            continue
        padding = "=" * ((4 - len(raw) % 4) % 4)
        try:
            decoded = base64.urlsafe_b64decode((raw + padding).encode("ascii")).decode("utf-8")
            data = json.loads(decoded)
        except Exception:
            continue
        if isinstance(data, dict):
            return data
    return {}


def _find_email(data: Any) -> str:
    if isinstance(data, dict):
        email = data.get("email")
        if isinstance(email, str) and email.strip():
            return email.strip()
        for value in data.values():
            found = _find_email(value)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _find_email(item)
            if found:
                return found
    return ""


def _token_email(token: str) -> str:
    payload = email_jwt(token)
    profile = payload.get("https://api.openai.com/profile", {})
    if isinstance(profile, dict) and profile.get("email"):
        return str(profile.get("email")).strip()
    return _find_email(payload)


def _token_user_id(token: str) -> str:
    payload = email_jwt(token)
    auth = payload.get("https://api.openai.com/auth", {})
    if isinstance(auth, dict):
        return str(auth.get("user_id") or auth.get("chatgpt_user_id") or "").strip()
    return str(payload.get("sub") or "").strip()


def _token_account_id(token: str) -> str:
    payload = email_jwt(token)
    auth = payload.get("https://api.openai.com/auth", {})
    if isinstance(auth, dict):
        return str(auth.get("chatgpt_account_id") or "").strip()
    return ""


def _team_session(proxies):
    session = requests.Session(proxies=proxies, impersonate="chrome110")
    session.headers.update({"Connection": "close"})
    session.timeout = 30
    return session


def _team_headers(access_token: str, account_id: str = "", json_body: bool = False) -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://chatgpt.com",
        "Referer": "https://chatgpt.com/",
    }
    if account_id:
        headers["chatgpt-account-id"] = account_id
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers


def _team_request(
    session,
    method: str,
    url: str,
    headers: Dict[str, str],
    json_body=None,
    proxies=None,
) -> Tuple[bool, Dict[str, Any], int, str]:
    last_error = ""
    for attempt in range(3):
        try:
            if attempt:
                time.sleep(1 + attempt)
            if method == "GET":
                resp = session.get(url, headers=headers, proxies=proxies, verify=_ssl_verify(), timeout=30)
            elif method == "POST":
                resp = session.post(url, headers=headers, json=json_body, proxies=proxies, verify=_ssl_verify(), timeout=30)
            elif method == "DELETE":
                resp = session.delete(url, headers=headers, json=json_body, proxies=proxies, verify=_ssl_verify(), timeout=30)
            else:
                raise ValueError(f"unsupported method: {method}")

            status = resp.status_code
            try:
                data = resp.json()
            except Exception:
                data = {}
            if 200 <= status < 300:
                return True, data if isinstance(data, dict) else {}, status, ""

            detail = ""
            if isinstance(data, dict):
                detail = str(data.get("detail") or data.get("error") or data.get("message") or "")
                err_obj = data.get("error")
                if isinstance(err_obj, dict):
                    detail = str(err_obj.get("message") or detail)
            last_error = detail or str(getattr(resp, "text", ""))[:500] or f"HTTP {status}"
            if status < 500:
                return False, data if isinstance(data, dict) else {}, status, last_error
        except Exception as exc:
            last_error = str(exc)
    return False, {}, 0, last_error


def _load_team_account_candidates(limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from utils import db_manager

        with db_manager.get_db_conn(as_dict=True) as conn:
            cursor = db_manager.get_cursor(conn, as_dict=True)
            order_clause = "RAND()" if db_manager.DB_TYPE == "mysql" else "RANDOM()"
            sql = (
                "SELECT id, email, access_token FROM team_accounts "
                "WHERE status = 1 AND access_token IS NOT NULL AND access_token != '' "
                f"ORDER BY {order_clause} LIMIT ?"
            )
            db_manager.execute_sql(cursor, sql, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
    except Exception as exc:
        print(f"[{cfg.ts()}] [WARNING] [TEAM] load team account candidates failed: {exc}")
        try:
            from utils import db_manager

            row = db_manager.get_random_team_account()
            return [row] if row else []
        except Exception:
            return []


def _get_team_accounts(access_token: str, proxies) -> Tuple[List[Dict[str, Any]], str]:
    session = _team_session(proxies)
    try:
        ok, data, status, err = _team_request(
            session,
            "GET",
            f"{TEAM_API_BASE}/accounts/check/v4-2023-04-27",
            _team_headers(access_token),
            proxies=proxies,
        )
        if not ok:
            return [], err or f"HTTP {status}"

        accounts_data = data.get("accounts", {})
        team_accounts = []
        if isinstance(accounts_data, dict):
            for account_id, info in accounts_data.items():
                account = info.get("account", {}) if isinstance(info, dict) else {}
                entitlement = info.get("entitlement", {}) if isinstance(info, dict) else {}
                if account.get("plan_type") == "team":
                    team_accounts.append({
                        "account_id": account_id,
                        "name": account.get("name", ""),
                        "role": account.get("account_user_role", ""),
                        "subscription_plan": entitlement.get("subscription_plan", ""),
                    })

        if team_accounts:
            return team_accounts, ""

        fallback_account_id = _token_account_id(access_token)
        if fallback_account_id:
            return [{"account_id": fallback_account_id, "name": "token-account", "role": ""}], ""
        return [], "no team account found in token"
    finally:
        try:
            session.close()
        except Exception:
            pass


def _send_team_invite_once(session, team_access_token: str, account_id: str, email: str, proxies):
    return _team_request(
        session,
        "POST",
        f"{TEAM_API_BASE}/accounts/{account_id}/invites",
        _team_headers(team_access_token, account_id, json_body=True),
        json_body={"email_addresses": [email], "role": "standard-user", "resend_emails": True},
        proxies=proxies,
    )


def _send_team_invite(team_access_token: str, account_id: str, email: str, proxies) -> Tuple[bool, Dict[str, Any], str]:
    session = _team_session(proxies)
    try:
        last_data: Dict[str, Any] = {}
        last_error = ""
        total_attempts = 1 + len(INVITE_RETRY_DELAYS)
        for attempt in range(total_attempts):
            if attempt:
                delay = INVITE_RETRY_DELAYS[attempt - 1]
                print(
                    f"[{cfg.ts()}] [WARNING] [TEAM] invite retry {attempt}/{len(INVITE_RETRY_DELAYS)} "
                    f"for {mask_email(email)} after {delay}s: {last_error}"
                )
                time.sleep(delay)

            ok, data, status, err = _send_team_invite_once(session, team_access_token, account_id, email, proxies)
            last_data = data
            if ok and not ("account_invites" in data and not data.get("account_invites")):
                return True, data, ""

            if ok:
                last_error = "invite response contains empty account_invites"
            else:
                last_error = err or f"HTTP {status}"

            if attempt < len(INVITE_RETRY_DELAYS):
                print(f"[{cfg.ts()}] [WARNING] [TEAM] invite attempt {attempt + 1}/{total_attempts} failed: {last_error}")

        return False, last_data, last_error
    finally:
        try:
            session.close()
        except Exception:
            pass


def _list_team_members(session, team_access_token: str, account_id: str, proxies) -> Tuple[List[Dict[str, Any]], str]:
    members = []
    offset = 0
    limit = 50
    while True:
        ok, data, status, err = _team_request(
            session,
            "GET",
            f"{TEAM_API_BASE}/accounts/{account_id}/users?limit={limit}&offset={offset}",
            _team_headers(team_access_token, account_id),
            proxies=proxies,
        )
        if not ok:
            return [], err or f"HTTP {status}"
        items = data.get("items", [])
        total = int(data.get("total") or 0)
        if isinstance(items, list):
            members.extend([item for item in items if isinstance(item, dict)])
        if not total or len(members) >= total:
            break
        offset += limit
    return members, ""


def _list_team_invites(session, team_access_token: str, account_id: str, proxies) -> Tuple[List[Dict[str, Any]], str]:
    ok, data, status, err = _team_request(
        session,
        "GET",
        f"{TEAM_API_BASE}/accounts/{account_id}/invites",
        _team_headers(team_access_token, account_id),
        proxies=proxies,
    )
    if not ok:
        return [], err or f"HTTP {status}"
    items = data.get("items", [])
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else [], ""


def sys_node_allocate(access_token: str, proxies=None) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """Invite the freshly registered account into one Team account.

    Returns (allocated, account_id, handle). The handle is later passed to
    sys_node_release so the cleanup uses the same Team admin token/account.
    """
    target_email = _token_email(access_token)
    target_user_id = _token_user_id(access_token)
    if not access_token or not target_email:
        print(f"[{cfg.ts()}] [WARNING] [TEAM] skip allocate: target token email not found")
        return False, None, None

    candidates = _load_team_account_candidates()
    if not candidates:
        print(f"[{cfg.ts()}] [WARNING] [TEAM] skip allocate: team account pool is empty")
        return False, None, None

    last_error = ""
    for team_row in candidates:
        team_token = str(team_row.get("access_token") or "").strip()
        team_email = str(team_row.get("email") or _token_email(team_token) or "").strip()
        if not team_token:
            continue

        accounts, err = _get_team_accounts(team_token, proxies)
        if not accounts:
            last_error = err
            print(f"[{cfg.ts()}] [WARNING] [TEAM] {mask_email(team_email)} has no usable team account: {err}")
            continue

        for account in accounts:
            account_id = str(account.get("account_id") or "").strip()
            if not account_id:
                continue

            ok, data, err = _send_team_invite(team_token, account_id, target_email, proxies)
            if ok:
                handle = {
                    "team_row_id": team_row.get("id"),
                    "team_email": team_email,
                    "team_access_token": team_token,
                    "team_account_id": account_id,
                    "member_email": target_email,
                    "member_user_id": target_user_id,
                    "invite_data": data,
                }
                print(f"[{cfg.ts()}] [SUCCESS] [TEAM] invited {mask_email(target_email)} via {mask_email(team_email)}")
                return True, account_id, handle

            last_error = err
            print(f"[{cfg.ts()}] [WARNING] [TEAM] invite failed via {mask_email(team_email)}: {err}")

    print(f"[{cfg.ts()}] [ERROR] [TEAM] allocate failed for {mask_email(target_email)}: {last_error}")
    return False, None, None


def sys_node_release(access_token: str, sys_handle_a=None, sys_handle_b=None, proxies=None) -> bool:
    """Undo sys_node_allocate by revoking the invite or removing the member."""
    handle = sys_handle_b if isinstance(sys_handle_b, dict) else {}
    team_token = str(handle.get("team_access_token") or "").strip()
    account_id = str(handle.get("team_account_id") or sys_handle_a or "").strip()
    target_email = str(handle.get("member_email") or _token_email(access_token) or "").strip()
    target_user_id = str(handle.get("member_user_id") or _token_user_id(access_token) or "").strip()

    if not team_token or not account_id or not target_email:
        return False

    session = _team_session(proxies)
    released = False
    try:
        invites, invite_err = _list_team_invites(session, team_token, account_id, proxies)
        if invite_err:
            print(f"[{cfg.ts()}] [WARNING] [TEAM] list invites failed before release: {invite_err}")
        for invite in invites:
            invite_email = str(invite.get("email_address") or invite.get("email") or "").strip()
            if invite_email.lower() != target_email.lower():
                continue
            ok, _, status, err = _team_request(
                session,
                "DELETE",
                f"{TEAM_API_BASE}/accounts/{account_id}/invites",
                _team_headers(team_token, account_id, json_body=True),
                json_body={"email_address": target_email},
                proxies=proxies,
            )
            if ok:
                released = True
                print(f"[{cfg.ts()}] [INFO] [TEAM] revoked invite for {mask_email(target_email)}")
            else:
                print(f"[{cfg.ts()}] [WARNING] [TEAM] revoke invite failed ({status}): {err}")

        members, member_err = _list_team_members(session, team_token, account_id, proxies)
        if member_err:
            print(f"[{cfg.ts()}] [WARNING] [TEAM] list members failed before release: {member_err}")
        for member in members:
            member_id = str(member.get("id") or member.get("user_id") or "").strip()
            member_email = str(member.get("email") or "").strip()
            matched = member_id and target_user_id and member_id == target_user_id
            matched = matched or (member_email and member_email.lower() == target_email.lower())
            if not matched or not member_id:
                continue
            ok, _, status, err = _team_request(
                session,
                "DELETE",
                f"{TEAM_API_BASE}/accounts/{account_id}/users/{member_id}",
                _team_headers(team_token, account_id),
                proxies=proxies,
            )
            if ok:
                released = True
                print(f"[{cfg.ts()}] [INFO] [TEAM] removed member {mask_email(target_email)}")
            else:
                print(f"[{cfg.ts()}] [WARNING] [TEAM] remove member failed ({status}): {err}")

        if not released:
            print(f"[{cfg.ts()}] [INFO] [TEAM] release skipped: {mask_email(target_email)} not found in team")
        return True
    except Exception as exc:
        print(f"[{cfg.ts()}] [WARNING] [TEAM] release failed: {exc}")
        return False
    finally:
        try:
            session.close()
        except Exception:
            pass
