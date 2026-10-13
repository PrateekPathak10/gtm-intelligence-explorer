import json

import pandas as pd
import streamlit as st

from app.config import settings
from app.schemas import ResearchRequest
from app.research import run_research
from app.providers.exa_provider import ProviderError


st.set_page_config(
    page_title="GTM Intelligence Explorer",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 GTM Intelligence Explorer")
st.caption(
    "Evidence-backed company discovery and enrichment | "
    "Exa research | Source-first prospect qualification"
)


with st.sidebar:
    st.header("Prospecting criteria")

    company_query = st.text_area(
        "Describe your ideal customer or enter a company",
        value=(
            "B2B SaaS companies using HubSpot or Salesforce, "
            "with 50–500 employees and signs of sales-team expansion"
        ),
        height=130,
    )

    objective = st.text_area(
        "Research objective",
        value=(
            "Evaluate whether the company could benefit from an "
            "AI-powered B2B GTM and outbound prospecting service."
        ),
        height=100,
    )

    employee_min = st.number_input(
        "Minimum employees",
        min_value=1,
        max_value=1_000_000,
        value=50,
    )

    employee_max = st.number_input(
        "Maximum employees",
        min_value=1,
        max_value=1_000_000,
        value=500,
    )

    technologies = st.multiselect(
        "Technology signals",
        [
            "HubSpot",
            "Salesforce",
            "Pipedrive",
            "Marketo",
            "Outreach",
            "Salesloft",
        ],
        default=["HubSpot", "Salesforce"],
    )

    growth_signals = st.multiselect(
        "Growth signals",
        [
            "Sales hiring",
            "Funding",
            "Geographic expansion",
            "Product launch",
            "Rapid hiring",
        ],
        default=["Sales hiring"],
    )

    max_results = st.slider(
        "Maximum research results",
        min_value=1,
        max_value=min(20, settings.max_search_results or 20),
        value=min(8, settings.max_search_results or 20),
    )

    search_button = st.button(
        "Research prospects",
        type="primary",
        use_container_width=True,
    )


col1, col2, col3 = st.columns(3)

col1.metric("Research provider", "Exa")
col2.metric("Enrichment provider", "MoltSets")
col3.metric("Data policy", "Evidence-first")

if settings.exa_api_key:
    st.success("Exa API key detected in application settings.")
else:
    st.error(
        "EXA_API_KEY is missing. Check your .env file and restart Streamlit."
    )

if not settings.moltsets_api_key:
    st.info(
        "MoltSets enrichment is not configured. "
        "The application will not invent enrichment data."
    )



if search_button:
    if not company_query.strip():
        st.error("Enter a company name or ideal-customer description.")

    elif employee_min > employee_max:
        st.error("Minimum employees cannot exceed maximum employees.")

    else:
        request = ResearchRequest(
            company_or_ideal_customer=company_query.strip(),
            research_objective=objective.strip(),
            employee_min=int(employee_min),
            employee_max=int(employee_max),
            technologies=technologies,
            growth_signals=growth_signals,
            max_results=int(max_results),
        )

        try:
            with st.spinner(
                "Researching public sources and normalizing company evidence..."
            ):
                prospects = run_research(request)

            if not prospects:
                st.warning(
                    "No results were returned. Try broadening your search criteria."
                )

            else:
                total = len(prospects)

                with_domains = sum(
                    bool(p.domain) for p in prospects
                )

                with_evidence = sum(
                    bool(p.evidence) for p in prospects
                )

                enriched = sum(
                    p.provider_status.get("moltsets") == "success"
                    for p in prospects
                )

                m1, m2, m3, m4 = st.columns(4)

                m1.metric("Prospects found", total)
                m2.metric("Domains identified", with_domains)
                m3.metric("With evidence", with_evidence)
                m4.metric("Enriched records", enriched)

                st.subheader("Research results")

                st.caption(
                    "Search results are candidate prospects, not automatically "
                    "qualified leads. Review the evidence before outreach."
                )

       
                rows = []

                for p in prospects:
                    evidence_urls = [
                        e.source_url
                        for e in p.evidence
                        if e.source_url
                    ]

                    rows.append(
                        {
                            "Company": p.company_name,
                            "Domain": p.domain or "Unavailable",
                            "Description": p.description or "Unavailable",
                            "Employee size": p.employee_size or "Unavailable",
                            "Industry": p.industry or "Unavailable",
                            "Technology signals": (
                                ", ".join(p.technology_signals)
                                or "Unverified"
                            ),
                            "Growth signals": (
                                ", ".join(p.growth_signals)
                                or "Unverified"
                            ),
                            "Confidence": p.confidence,
                            "Fit status": p.fit_status,
                            "MoltSets status": p.provider_status.get(
                                "moltsets", "unknown"
                            ),
                            "Source count": len(evidence_urls),
                        }
                    )

                results_df = pd.DataFrame(rows)

                st.dataframe(
                    results_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Domain": st.column_config.TextColumn(
                            "Domain",
                            help="Domain extracted from a search-result URL.",
                        ),
                        "Description": st.column_config.TextColumn(
                            "Description / evidence",
                            width="large",
                        ),
                        "Source count": st.column_config.NumberColumn(
                            "Sources",
                            help="Number of evidence URLs available for this prospect.",
                        ),
                    },
                )

           
                st.subheader("Company evidence and details")

                for index, p in enumerate(prospects, start=1):
                    heading = (
                        f"{index}. {p.company_name} · "
                        f"{p.domain or 'Domain unavailable'}"
                    )

                    with st.expander(heading):
                        st.markdown("**Description / search evidence**")
                        st.write(p.description or "No description returned.")

                        left, right = st.columns(2)

                        with left:
                            st.markdown("**Company information**")
                            st.write(
                                {
                                    "Industry": p.industry or "Unavailable",
                                    "Target market": (
                                        p.target_market or "Unavailable"
                                    ),
                                    "Employee size": (
                                        p.employee_size or "Unavailable"
                                    ),
                                    "Confidence": p.confidence,
                                    "Fit status": p.fit_status,
                                }
                            )

                        with right:
                            st.markdown("**Potential GTM signals**")
                            st.write(
                                {
                                    "Technology signals": (
                                        p.technology_signals or ["Unverified"]
                                    ),
                                    "Growth signals": (
                                        p.growth_signals or ["Unverified"]
                                    ),
                                    "Potential GTM opportunity": (
                                        p.potential_gtm_opportunity
                                        or "Needs further research"
                                    ),
                                }
                            )

                        st.markdown("**Sources**")

                        if p.evidence:
                            for evidence_index, evidence in enumerate(
                                p.evidence, start=1
                            ):
                                st.markdown(
                                    f"**Evidence {evidence_index}** — "
                                    f"{evidence.status}"
                                )

                                st.write(
                                    evidence.snippet
                                    or evidence.claim
                                    or "No text available."
                                )

                                if evidence.source_url:
                                    st.markdown(
                                        f"[Open source]({evidence.source_url})"
                                    )

                                if evidence.published_date:
                                    st.caption(
                                        "Published: "
                                        f"{evidence.published_date}"
                                    )

                                st.divider()

                        else:
                            st.warning(
                                "No source-backed evidence was returned."
                            )

                        st.markdown("**Provider status**")
                        st.json(p.provider_status)

                        st.markdown("**Structured record (JSON)**")
                        st.json(p.model_dump())

                st.subheader("Export results")

                json_payload = json.dumps(
                    [p.model_dump() for p in prospects],
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )

                csv_payload = results_df.to_csv(index=False)

                download_col1, download_col2 = st.columns(2)

                with download_col1:
                    st.download_button(
                        "Download JSON",
                        data=json_payload,
                        file_name="gtm_research_results.json",
                        mime="application/json",
                        use_container_width=True,
                    )

                with download_col2:
                    st.download_button(
                        "Download CSV",
                        data=csv_payload,
                        file_name="gtm_prospects.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

        except ProviderError as exc:
            st.error(str(exc))

        except Exception as exc:
            st.error(
                f"Research failed safely ({exc.__class__.__name__}). "
                "Check configuration and application logs."
            )


st.divider()
st.subheader("Data quality rules")

st.markdown(
    """
- **Source-backed:** The claim appears in retrieved source content; verify the source before relying on it.
- **Provider-reported:** The information was returned by an authorized enrichment provider.
- **Inferred:** A reasoned interpretation, not a confirmed company fact.
- **Unavailable / Unverified:** The application could not establish the field reliably.
- Search-result titles do not independently prove legal company identity.
- Technology usage, employee count, decision-makers, and growth signals should
  only be presented as confirmed when supported by relevant evidence.
- A company appearing in search results does not prove it matches every ICP filter.
- Provider errors and missing enrichment are reported rather than replaced with fabricated data.
"""
)