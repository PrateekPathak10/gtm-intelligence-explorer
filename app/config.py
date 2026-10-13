
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env from the project root, regardless of the launch directory.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)


@dataclass(frozen=True)
class Settings:
    exa_api_key: str | None = os.getenv("EXA_API_KEY")
    moltsets_api_key: str | None = os.getenv("MOLTSETS_API_KEY")
    moltsets_base_url: str | None = os.getenv("MOLTSETS_BASE_URL")
    moltsets_search_companies_path: str | None = os.getenv(
        "MOLTSETS_SEARCH_COMPANIES_PATH"
    )
    request_timeout_seconds: float = float(
        os.getenv("REQUEST_TIMEOUT_SECONDS", "25")
    )
    max_search_results: int = int(
        os.getenv("MAX_SEARCH_RESULTS", "10")
    )


settings = Settings()
