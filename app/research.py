import re

from app.providers.exa_provider import ExaResearchProvider
from app.providers.moltsets_adapter import (
    MoltSetsAdapter,
    EnrichmentNotConfigured,
)
from app.normalization import (
    normalize_result,
    deduplicate_prospects,
    is_likely_company_result,
)
from app.schemas import ResearchRequest


def build_query(request: ResearchRequest) -> str:
    parts = [
        request.company_or_ideal_customer,
        "Find real B2B companies that could be sales prospects.",
        "Prioritize official company websites, about pages, product pages, "
        "technology pages, leadership pages, and careers pages.",
        "Return source-backed facts and source URLs.",
        "Do not invent employee counts, CRM usage, contacts, or decision-makers.",
    ]

    if request.employee_min is not None or request.employee_max is not None:
        parts.append(
            f"Target companies with {request.employee_min or 'any'} to "
            f"{request.employee_max or 'any'} employees. "
            "Prefer exact employee counts and identify conflicting estimates."
        )

    if request.technologies:
        parts.append(
            "Look for evidence that the company itself uses these technologies: "
            + ", ".join(request.technologies)
            + ". A general mention, comparison, or integration listing alone "
            "does not prove usage."
        )

    if request.growth_signals:
        parts.append(
            "Look for explicit evidence of these growth signals: "
            + ", ".join(request.growth_signals)
            + "."
        )

    if request.research_objective:
        parts.append("Research objective: " + request.research_objective)

    parts.append(
        "Avoid treating articles, listicles, directories, and comparison pages "
        "as the company itself. Return the strongest evidence available."
    )

    return " ".join(parts)


def _employee_bounds(value: str | None) -> tuple[int | None, int | None]:
    """
    Return (lower, upper).

    '67 employees' -> (67, 67)
    '51–200 employees' -> (51, 200)
    Unknown values -> (None, None)
    """
    if not value:
        return None, None

    numbers = re.findall(r"\d[\d,]*", value)
    numbers = [int(number.replace(",", "")) for number in numbers]

    if not numbers:
        return None, None

    if len(numbers) >= 2:
        return min(numbers[0], numbers[1]), max(numbers[0], numbers[1])

    return numbers[0], numbers[0]


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _growth_matches_requested(
    requested: set[str],
    found: set[str],
) -> bool:
    """
    Map UI labels to labels extracted from source evidence.

    A selected growth criterion is not considered verified merely because
    another unrelated growth signal was found.
    """
    aliases = {
        "sales hiring": {"hiring activity"},
        "rapid hiring": {"hiring activity", "employee growth"},
        "funding": {"funding"},
        "geographic expansion": {"expansion"},
        "product launch": {"product launch"},
    }

    normalized_found = {_normalize_label(item) for item in found}

    for requested_label in requested:
        normalized_requested = _normalize_label(requested_label)

        acceptable = aliases.get(
            normalized_requested,
            {normalized_requested},
        )

        if any(_normalize_label(item) in normalized_found for item in acceptable):
            return True

    return False


def _apply_fit_status(prospect, request: ResearchRequest) -> None:
    """
    Assign a conservative qualification status.

    Search results are candidate prospects, not automatically qualified leads.
    """
    warning = prospect.provider_status.get("data_quality_warning")

    if warning:
        prospect.fit_status = "Needs review - conflicting employee evidence"
        return

    lower, upper = _employee_bounds(prospect.employee_size)

    minimum = request.employee_min
    maximum = request.employee_max

    if lower is None or upper is None:
        prospect.fit_status = "Needs review - employee count unverified"
        return

    # A range entirely below or above the requested range is a mismatch.
    if minimum is not None and upper < minimum:
        prospect.fit_status = "Outside employee range"
        return

    if maximum is not None and lower > maximum:
        prospect.fit_status = "Outside employee range"
        return

    exact_count = lower == upper

    # A broad employee band overlapping the ICP is not proof of a match.
    if not exact_count:
        prospect.fit_status = "Potential fit - employee range estimate"
        return

    # Exact count must lie within both selected boundaries.
    if minimum is not None and lower < minimum:
        prospect.fit_status = "Outside employee range"
        return

    if maximum is not None and upper > maximum:
        prospect.fit_status = "Outside employee range"
        return

    requested_technologies = {
        item.strip()
        for item in request.technologies
        if item.strip()
    }
    found_technologies = {
        item.strip()
        for item in prospect.technology_signals
        if item.strip()
    }

    # If CRM usage is part of the ICP, require at least one selected
    # technology to be supported by retrieved evidence.
    if requested_technologies and not {
        _normalize_label(item) for item in requested_technologies
    }.intersection({_normalize_label(item) for item in found_technologies}):
        prospect.fit_status = "Needs review - technology not verified"
        return

    requested_growth = {
        item.strip()
        for item in request.growth_signals
        if item.strip()
    }
    found_growth = {
        item.strip()
        for item in prospect.growth_signals
        if item.strip()
    }

    if requested_growth and not _growth_matches_requested(
        requested_growth,
        found_growth,
    ):
        prospect.fit_status = "Needs review - growth signal not verified"
        return

    prospect.fit_status = "Potential fit - verify evidence"


def run_research(request: ResearchRequest, exa=None, moltsets=None) -> list:
    exa = exa or ExaResearchProvider()
    moltsets = moltsets or MoltSetsAdapter()

    results = exa.search(
        build_query(request),
        num_results=request.max_results,
    )

    company_results = [
        result
        for result in results
        if is_likely_company_result(result)
    ]

    prospects = deduplicate_prospects([
        normalize_result(result, request.research_objective)
        for result in company_results
    ])

    for prospect in prospects:
        _apply_fit_status(prospect, request)

        # Don't send records without a usable company domain to enrichment.
        if not prospect.domain:
            prospect.provider_status["moltsets"] = "skipped_no_domain"
            continue

        try:
            enriched = moltsets.enrich_company(
                prospect.company_name,
                prospect.domain,
            )

            prospect.provider_status["moltsets"] = "success"

            if isinstance(enriched, dict):
                prospect.provider_status["moltsets_data"] = enriched.get("data")

        except EnrichmentNotConfigured:
            prospect.provider_status["moltsets"] = "not_configured"

        except Exception as exc:
            # An enrichment failure should not stop other prospects.
            prospect.provider_status["moltsets"] = "error"
            prospect.provider_status["moltsets_error"] = (
                f"{exc.__class__.__name__}: {str(exc)[:250]}"
            )

    return prospects