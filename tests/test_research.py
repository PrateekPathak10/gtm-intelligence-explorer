from app.research import build_query
from app.schemas import ResearchRequest

def test_build_query_includes_criteria():
    q = build_query(ResearchRequest(
        company_or_ideal_customer="B2B SaaS",
        employee_min=50, employee_max=500,
        technologies=["HubSpot"], growth_signals=["Sales hiring"]
    ))
    assert "HubSpot" in q
    assert "Sales hiring" in q
    assert "50 to 500 employees" in q
