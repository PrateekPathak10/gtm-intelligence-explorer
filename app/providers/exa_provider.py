from datetime import date
from app.config import settings

class ProviderError(RuntimeError):
    pass

class ExaResearchProvider:
    def __init__(self, client=None):
        if client is not None:
            self.client = client
        elif settings.exa_api_key:
            try:
                from exa_py import Exa
            except ImportError as exc:
                raise ProviderError("Install dependencies with `pip install -r requirements.txt` to use Exa.") from exc
            self.client = Exa(api_key=settings.exa_api_key)
        else:
            self.client = None

    def search(self, query: str, num_results: int = 8) -> list[dict]:
        if not self.client:
            raise ProviderError("EXA_API_KEY is not configured. Add it to .env and restart the app.")
        try:
            response = self.client.search(
                query,
                type="auto",
                num_results=max(1, min(num_results, 20)),
                contents={"highlights": {"num_sentences": 3}}
            )
            output = []
            for item in getattr(response, "results", []) or []:
                highlights = getattr(item, "highlights", None) or []
                output.append({
                    "title": getattr(item, "title", None),
                    "url": getattr(item, "url", None),
                    "published_date": getattr(item, "published_date", None),
                    "author": getattr(item, "author", None),
                    "text": " ".join(str(x) for x in highlights) if highlights else None,
                })
            return output
        except Exception as exc:
            message = str(exc).lower()
            if "429" in message or "rate" in message:
                raise ProviderError("Exa rate limit reached. Wait before retrying.") from exc
            if "timeout" in message or "timed out" in message:
                raise ProviderError("Exa request timed out. Try again.") from exc
            raise ProviderError(f"Exa research failed: {exc.__class__.__name__}. Check the key, network and Exa status.") from exc
