import re
from urllib.parse import urlparse

from app.schemas import Prospect, Evidence


ARTICLE_TITLE_PATTERNS = [
    r"\bcase study\b",
    r"\bcustomer story\b",
    r"\blessons from\b",
    r"\bgrowth journey\b",
    r"\bmigration\b",
    r"\bimplementation case\b",
    r"\bhow .+ rebuilt\b",
    r"\bpipeline in \d+\b",
    r"\btop \d+\b",
    r"\bversus\b",
    r"\bcomparison\b",
]

EDITORIAL_PATHS = {
    "blog", "blogs", "news", "resources", "resource",
    "case-studies", "customer-stories", "guides",
    "articles", "learn", "insights",
}

AGGREGATOR_HOSTS = {
    "linkedin.com",
    "echoloc.ai",
    "crunchbase.com",
    "zoominfo.com",
    "apollo.io",
    "theorg.com",
    "growjo.com",
    "owler.com",
}

GENERIC_TITLES = {
    "about us", "about", "home", "company", "overview",
    "our company", "us", "welcome", "website",
    "official website",
}

GROWTH_PATTERNS = [
    (
        r"\b(?:actively hiring|hiring|open roles|job postings|careers page)\b",
        "Hiring activity",
    ),
    (
        r"\b(?:year[- ]over[- ]year|YoY)\s*(?:growth)?\s*[:+]?\s*\d+(?:\.\d+)?%",
        "Employee growth",
    ),
    (
        r"\b(?:raised|raises|funding round|Series [A-F]|seed funding)\b",
        "Funding",
    ),
    (
        r"\b(?:expanding|new office|new market|international expansion)\b",
        "Expansion",
    ),
    (
        r"\b(?:launches|launched|product launch|new product)\b",
        "Product launch",
    ),
]

INDUSTRIES = [
    "Software Development",
    "Information Technology",
    "Financial Services",
    "Computer Software",
    "Marketing and Advertising",
    "Internet",
    "Telecommunications",
    "Business Consulting",
]

TECHNOLOGY_USAGE_PATTERNS = {
    "HubSpot": (
        r"\b(?:uses|using|used|powered by|implemented|integrates with|"
        r"runs on|adopted|deployed)\s+(?:the\s+)?HubSpot\b"
        r"|\bHubSpot\s+(?:CRM|integration|implementation)\b"
        r"|\b(?:HubSpot CRM|CRM powered by HubSpot)\b"
    ),
    "Salesforce": (
        r"\b(?:uses|using|used|powered by|implemented|integrates with|"
        r"runs on|adopted|deployed)\s+(?:the\s+)?Salesforce\b"
        r"|\bSalesforce\s+(?:CRM|integration|implementation)\b"
        r"|\b(?:Salesforce CRM|CRM powered by Salesforce)\b"
    ),
    "Zoho": r"\b(?:uses|using|powered by|implemented)\s+Zoho\b",
    "Zendesk": r"\b(?:uses|using|powered by|implemented)\s+Zendesk\b",
    "Intercom": r"\b(?:uses|using|powered by|implemented)\s+Intercom\b",
    "Salesloft": r"\b(?:uses|using|powered by|implemented)\s+Salesloft\b",
    "Apollo": r"\b(?:uses|using|powered by|implemented)\s+Apollo\b",
    "ZoomInfo": r"\b(?:uses|using|powered by|implemented)\s+ZoomInfo\b",
    "Outreach": r"\b(?:uses|using|powered by|implemented)\s+Outreach\b",
    "Pipedrive": r"\b(?:uses|using|powered by|implemented)\s+Pipedrive\b",
    "Marketo": r"\b(?:uses|using|powered by|implemented)\s+Marketo\b",
    "Freshworks": r"\b(?:uses|using|powered by|implemented)\s+Freshworks\b",
    "Dynamics 365": r"\b(?:uses|using|powered by|implemented)\s+Dynamics 365\b",
    "ServiceNow": r"\b(?:uses|using|powered by|implemented)\s+ServiceNow\b",
    "Gong": r"\b(?:uses|using|powered by|implemented)\s+Gong\b",
    "Clari": r"\b(?:uses|using|powered by|implemented)\s+Clari\b",
    "6sense": r"\b(?:uses|using|powered by|implemented)\s+6sense\b",
}


def _domain(url: str | None) -> str | None:
    if not url:
        return None

    try:
        parsed = urlparse(url if "://" in url else "https://" + url)
        host = parsed.hostname
        return host.lower().removeprefix("www.") if host else None
    except (ValueError, AttributeError):
        return None


def _clean_domain(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip().strip(".,;()[]<>")

    match = re.search(
        r"(?i)(?:https?://)?(?:www\.)?"
        r"([a-z0-9][a-z0-9.-]*\.[a-z]{2,})",
        value,
    )

    if not match:
        return None

    return match.group(1).lower().removeprefix("www.")


def _is_aggregator(host: str | None) -> bool:
    if not host:
        return False

    return any(
        host == domain or host.endswith("." + domain)
        for domain in AGGREGATOR_HOSTS
    )


def _canonical_domain(
    url: str | None,
    snippet: str | None,
) -> str | None:
    """Prefer a company website explicitly identified in retrieved text."""

    if snippet:
        patterns = [
            r"(?im)^\s*[-•]?\s*(?:official\s+)?"
            r"(?:company\s+)?(?:homepage|website|domain)\s*:\s*(.+?)\s*$",
            r"(?im)^\s*[-•]?\s*Homepage\s+(.+?)\s*$",
        ]

        for pattern in patterns:
            match = re.search(pattern, snippet)
            if match:
                candidate = _clean_domain(match.group(1))
                if candidate and not _is_aggregator(candidate):
                    return candidate

        # Example: "saaslabs.co LinkedIn".
        match = re.search(
            r"(?i)\b([a-z0-9][a-z0-9.-]+\.[a-z]{2,})\s+LinkedIn\b",
            snippet,
        )
        if match:
            candidate = _clean_domain(match.group(1))
            if candidate and not _is_aggregator(candidate):
                return candidate

    source_domain = _domain(url)

    if _is_aggregator(source_domain):
        return None

    return source_domain


def _company_name(
    title: str,
    snippet: str | None,
    url: str | None,
) -> str:
    """Extract a plausible company name from the result title or text."""

    raw_title = (title or "").strip()
    parts = re.split(r"\s+(?:\||—|–)\s+", raw_title)

    name = parts[0].strip() if parts else ""
    name = re.sub(r"(?i)^about\s+", "", name).strip()
    name = re.sub(
        r"(?i)\s+Tech Stack(?:\s*\(.*\))?$",
        "",
        name,
    ).strip()

    if name.lower() in GENERIC_TITLES or len(name) < 2:
        name = ""

    if snippet:
        patterns = [
            r"(?im)^\s*([A-Z][A-Za-z0-9&.'’()-]*"
            r"(?:\s+[A-Z0-9][A-Za-z0-9&.'’()-]*){0,5})\s+"
            r"(?:is|are|helps|builds|provides|develops|employs|"
            r"offers|creates|was founded|specializes|specialises)\b",
            r"(?im)^\s*Company\s*:\s*([^\n|]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, snippet)
            if match:
                candidate = match.group(1).strip(" .,:;")
                if candidate.lower() not in GENERIC_TITLES and len(candidate) > 1:
                    if not name:
                        name = candidate
                    break

        # Example: "About Our Company | Canopy".
        if not name:
            for part in parts[1:]:
                candidate = re.sub(
                    r"(?i)^about\s+",
                    "",
                    part.strip(),
                ).strip()

                if candidate and candidate.lower() not in GENERIC_TITLES:
                    name = candidate
                    break

    if not name:
        domain = _canonical_domain(url, snippet) or _domain(url)
        if domain and not _is_aggregator(domain):
            label = domain.split(".")[0]
            name = label[:1].upper() + label[1:]

    return name or "Unknown company"



def _extract_employee_size(text: str) -> str | None:
    if not text:
        return None

    exact_patterns = [
        r"(?i)\bemploys\s+([\d,]+)\s+people\b",
        r"(?i)\bhas\s+([\d,]+)\s+employees\b",
        r"(?i)\bteam\s+of\s+([\d,]+)\s+(?:employees|people|staff)\b",
        r"(?im)^\s*[-•]?\s*Employees\s*:\s*([\d,]+)\s*$",
        r"(?i)\b([\d,]+)\s+employees\b",
    ]

    text_without_ranges = re.sub(
        r"(?i)\b\d[\d,]*\s*[-–—]\s*\d[\d,]*\s+employees\b",
        " ",
        text,
    )

    for pattern in exact_patterns:
        match = re.search(pattern, text_without_ranges)
        if match:
            count = int(match.group(1).replace(",", ""))
            if count > 0:
                return f"{count} employees"

    # If no exact count exists, retain the reported range.
    range_patterns = [
        r"(?i)\b(\d[\d,]*)\s*[-–—]\s*(\d[\d,]*)\s+employees\b",
        r"(?im)^\s*[-•]?\s*Company Size\s*:\s*(\d[\d,]*)\s*[-–—]\s*(\d[\d,]*)",
    ]

    for pattern in range_patterns:
        match = re.search(pattern, text)
        if match:
            low = int(match.group(1).replace(",", ""))
            high = int(match.group(2).replace(",", ""))
            return f"{min(low, high)}–{max(low, high)} employees"

    return None

def _employee_evidence_conflicts(text: str) -> bool:
    """
    Detect a contradictory exact employee count and company-size range.
    This is a warning, not a claim about which source is correct.
    """
    exact_patterns = [
        r"(?i)\bEmployees?\s*:\s*(\d[\d,]*)\b",
        r"(?i)\bemploys\s+(\d[\d,]*)\s+(?:people|employees)\b",
        r"(?i)\bhas\s+(\d[\d,]*)\s+employees\b",
    ]

    exact_counts = []
    for pattern in exact_patterns:
        exact_counts.extend(
            int(value.replace(",", ""))
            for value in re.findall(pattern, text)
        )

    range_patterns = [
        r"(?i)\b(?:company\s+size|employee\s+size)\s*:\s*"
        r"(\d[\d,]*)\s*[-–—]\s*(\d[\d,]*)\s*employees?\b",
        r"(?i)\b(\d[\d,]*)\s*[-–—]\s*(\d[\d,]*)\s+employees\b",
    ]

    ranges = []
    for pattern in range_patterns:
        for low, high in re.findall(pattern, text):
            ranges.append((
                int(low.replace(",", "")),
                int(high.replace(",", "")),
            ))

    for count in exact_counts:
        for low, high in ranges:
            if not low <= count <= high:
                return True

    return False


def _extract_technology_signals(text: str) -> list[str]:
    """Return only technologies supported by usage-like wording."""

    if not text:
        return []

    found = []
    for technology, pattern in TECHNOLOGY_USAGE_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(technology)

    return found


def _extract_growth_signals(text: str) -> list[str]:
    found = []

    for pattern, label in GROWTH_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            if label not in found:
                found.append(label)

    return found


def _extract_industry(text: str) -> str | None:
    match = re.search(
        r"(?i)\bIndustry\s*:\s*([^\n.;|]+)",
        text,
    )

    if match:
        value = match.group(1).strip()
        if value:
            return value

    for industry in INDUSTRIES:
        if re.search(re.escape(industry), text, flags=re.IGNORECASE):
            return industry

    return None


def _extract_target_market(text: str) -> str | None:
    patterns = [
        r"(?i)\b(?:serves|serving|for)\s+"
        r"((?:B2B\s+)?(?:sales|marketing|support|finance|accounting|"
        r"revenue|customer success|HR|human resources|enterprise|"
        r"small businesses|mid-market|SaaS)\s+teams?)\b",
        r"(?i)\b(?:target market|target audience|customers are)\s*:\s*"
        r"([^\n.;|]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()[:180]

    return None


def _extract_decision_makers(text: str) -> list[dict]:
    """
    Extract cautiously from source text. These records still need review:
    text matching alone cannot guarantee that a person/title pairing is valid.
    """
    people = []

    role_pattern = re.compile(
        r"\b([A-Z][A-Za-z.'’\-]+"
        r"(?:\s+[A-Z][A-Za-z.'’\-]+){1,3})\s*:?\s+"
        r"(CEO|CTO|CFO|COO|CMO|CRO|"
        r"Chief [A-Za-z &/-]+ Officer|"
        r"VP [A-Za-z &/-]+|Vice President [A-Za-z &/-]+|"
        r"Head of [A-Za-z &/-]+|Director of [A-Za-z &/-]+|"
        r"Co-Founder|Founder)\b"
    )

    for match in role_pattern.finditer(text):
        person = {
            "name": match.group(1).strip(),
            "title": match.group(2).strip(),
            "status": "source-backed",
        }

        if person not in people:
            people.append(person)

    return people[:10]


def _extract_contact_information(text: str) -> list[dict]:
    contacts = []

    for email in re.findall(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        flags=re.IGNORECASE,
    ):
        item = {
            "type": "email",
            "value": email,
            "status": "source-backed",
        }
        if item not in contacts:
            contacts.append(item)

    for phone in re.findall(
        r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?"
        r"(?:\(?\d{2,4}\)?[\s.-]?)"
        r"\d{3,4}[\s.-]?\d{3,4}(?!\w)",
        text,
    ):
        cleaned = re.sub(r"\s+", " ", phone).strip()

        if len(re.sub(r"\D", "", cleaned)) >= 8:
            item = {
                "type": "phone",
                "value": cleaned,
                "status": "source-backed",
            }
            if item not in contacts:
                contacts.append(item)

    return contacts[:10]







def is_likely_company_result(result: dict) -> bool:
    """Reject obvious articles, migration stories, case studies, and listicles."""

    title = str(result.get("title") or "").strip()
    url = str(result.get("url") or "").strip()

    if not title or not url:
        return False

    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path.lower()
    except (ValueError, AttributeError):
        return False

    if parsed.scheme not in {"http", "https"} or not host:
        return False

    # Pages commonly containing articles instead of company profiles.
    blocked_paths = (
        "/blog/", "/blogs/", "/resources/", "/case-study/",
        "/case-studies/", "/customer-stories/", "/stories/customers/",
        "/press-releases/", "/news/", "/articles/", "/insights/",
        "/events/",
    )

    if any(term in path for term in blocked_paths):
        return False

    # Reject editorial titles, including CRM migration stories.
    editorial_patterns = (
        r"\bcase\s+stud(?:y|ies)\b",
        r"\bcustomer\s+stor(?:y|ies)\b",
        r"\bmigration\b",
        r"\bmigrating\b",
        r"\bmigrated\b",
        r"\bimplementation\s+story\b",
        r"\btop\s+\d+\b",
        r"\bbest\s+.+\s+(tools|software|platforms|companies)\b",
        r"\bversus\b",
        r"\bvs\.?\b",
        r"\bpress\s+release\b",
        r"^\s*how\s+to\b",
        r"^\s*how\b.*\b(helped|uses|used|grew|scaled|transformed)\b",
        r"\bfrom\s+.{2,}\s+to\s+.{2,}\s+(migration|migrating)\b",
    )

    if any(
        re.search(pattern, title, re.IGNORECASE)
        for pattern in editorial_patterns
    ):
        return False

    # Reject known publishing/search platforms.
    blocked_hosts = {
        "google.com",
        "www.google.com",
        "bing.com",
        "www.bing.com",
        "medium.com",
        "www.medium.com",
    }

    if host in blocked_hosts or host.endswith(".medium.com"):
        return False

    # Reject titles clearly attributed to a publisher or agency.
    if re.search(
        r"\s[-|–]\s(iceberg revops|hubspot blog|medium|forbes)$",
        title,
        re.IGNORECASE,
    ):
        return False

    return True

def normalize_result(item: dict, objective: str = "") -> Prospect:
    title = (item.get("title") or "").strip()
    url = item.get("url")
    snippet = (item.get("text") or "").strip() or None

    company = _company_name(title, snippet, url)
    domain = _canonical_domain(url, snippet)

    source_text = f"{title}\n{snippet or ''}"

    description = snippet
    if description and len(description) > 700:
        description = description[:697].rstrip() + "..."

    evidence = []
    if url:
        evidence.append(
            Evidence(
                claim=snippet or f"Search result: {title}",
                source_url=url,
                published_date=item.get("published_date"),
                status="source-backed",
                snippet=snippet,
            )
        )

    provider_status = {
        "exa": "success",
        "moltsets": "not_configured",
    }

    if _employee_evidence_conflicts(source_text):
        provider_status["data_quality_warning"] = (
            "Conflicting employee-count evidence found in retrieved text. "
            "Verify the count against the original source."
        )

    return Prospect(
        company_name=company,
        domain=domain,
        description=description,
        industry=_extract_industry(source_text),
        target_market=_extract_target_market(source_text),
        employee_size=_extract_employee_size(source_text),        technology_signals=_extract_technology_signals(source_text),
        growth_signals=_extract_growth_signals(source_text),
        decision_makers=_extract_decision_makers(source_text),
        contact_information=_extract_contact_information(source_text),
        evidence=evidence,
        confidence="medium" if snippet and url else "low",
        fit_status="Needs review",
        provider_status=provider_status,
    )


def deduplicate_prospects(prospects: list[Prospect]) -> list[Prospect]:
    seen = set()
    output = []

    for prospect in prospects:
        key = (prospect.domain or prospect.company_name).lower().strip()

        if key not in seen:
            seen.add(key)
            output.append(prospect)

    return output