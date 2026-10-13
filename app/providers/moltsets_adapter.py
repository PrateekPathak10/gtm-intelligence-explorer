"""
MoltSets provider adapter boundary.

The assignment asks us to verify the exact service, credentials, endpoint schemas and
free-tier limits before integrating. Do not guess undocumented endpoints or pretend
a mock response is real enrichment. Configure the endpoint only after confirming it
against Outmate's docs/account.
"""
import requests
from app.config import settings

class EnrichmentNotConfigured(RuntimeError):
    pass

class MoltSetsAdapter:
    def enrich_company(self, company_name: str, domain: str | None = None) -> dict:
        if not settings.moltsets_api_key or not settings.moltsets_base_url or not settings.moltsets_search_companies_path:
            raise EnrichmentNotConfigured(
                "MoltSets enrichment is not configured. Confirm provider access, endpoint, "
                "authentication and request schema with Outmate before enabling it."
            )
        url = settings.moltsets_base_url.rstrip("/") + "/" + settings.moltsets_search_companies_path.lstrip("/")
        payload = {"company_name": company_name}
        if domain:
            payload["domain"] = domain
        try:
            response = requests.post(
                url, json=payload,
                headers={"Authorization": f"Bearer {settings.moltsets_api_key}", "Content-Type": "application/json"},
                timeout=settings.request_timeout_seconds,
            )
            if response.status_code == 429:
                raise RuntimeError("MoltSets rate limit reached.")
            response.raise_for_status()
            return {"status": "provider-reported", "data": response.json()}
        except requests.Timeout as exc:
            raise RuntimeError("MoltSets request timed out.") from exc
        except requests.RequestException as exc:
            raise RuntimeError(f"MoltSets request failed ({exc.__class__.__name__}).") from exc
