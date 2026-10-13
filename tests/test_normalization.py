from app.normalization import normalize_result, deduplicate_prospects

def test_normalize_result_extracts_domain_and_source():
    p = normalize_result({"title": "Acme | Company", "url": "https://www.acme.com/about", "text": "Acme builds B2B software."})
    assert p.domain == "acme.com"
    assert p.company_name == "Acme"
    assert p.evidence[0].source_url == "https://www.acme.com/about"

def test_missing_fields_are_not_fabricated():
    p = normalize_result({"title": "Unknown company", "url": None, "text": None})
    assert p.employee_size is None
    assert p.decision_makers == []
    assert p.contact_information == []
    assert p.confidence == "low"

def test_deduplicate_by_domain():
    a = normalize_result({"title": "Acme", "url": "https://acme.com"})
    b = normalize_result({"title": "Acme Inc", "url": "https://www.acme.com/about"})
    assert len(deduplicate_prospects([a, b])) == 1




from app.normalization import is_likely_company_result


def test_rejects_case_study_as_prospect():
    result = {
        "title": "HubSpot CRM Implementation Case Study",
        "url": "https://example.com/case-study",
    }
    assert not is_likely_company_result(result)


def test_rejects_migration_article_as_prospect():
    result = {
        "title": "Maki: HubSpot to Salesforce Migration",
        "url": "https://example.com/story",
    }
    assert not is_likely_company_result(result)


def test_accepts_company_about_page():
    result = {
        "title": "Acme | Company",
        "url": "https://www.acme.com/about",
    }
    assert is_likely_company_result(result)


def test_rejects_missing_url():
    assert not is_likely_company_result({
        "title": "Acme",
        "url": None,
    })

def test_extracts_employee_count():
    from app.normalization import normalize_result

    p = normalize_result({
        "title": "Acme | Company",
        "url": "https://acme.com/about",
        "text": "Acme has 70 employees and is growing its team.",
    })

    assert p.employee_size == "70 employees"


def test_extracts_employee_range():
    from app.normalization import normalize_result

    p = normalize_result({
        "title": "Acme | Company",
        "url": "https://acme.com/about",
        "text": "The company has 201-500 employees.",
    })

    assert p.employee_size == "201–500 employees"


def test_does_not_infer_employee_count_when_missing():
    from app.normalization import normalize_result

    p = normalize_result({
        "title": "Acme | Company",
        "url": "https://acme.com/about",
        "text": "Acme builds software for sales teams.",
    })

    assert p.employee_size is None


def test_extracts_explicit_technology_usage():
    from app.normalization import normalize_result

    p = normalize_result({
        "title": "Acme | Company",
        "url": "https://acme.com/about",
        "text": "The company uses HubSpot CRM.",
    })

    assert "HubSpot" in p.technology_signals


def test_does_not_claim_technology_usage_from_bare_mention():
    from app.normalization import normalize_result

    p = normalize_result({
        "title": "Acme | Company",
        "url": "https://acme.com/about",
        "text": "HubSpot and Salesforce are popular CRM products.",
    })

    assert p.technology_signals == []


def test_does_not_use_linkedin_as_company_domain():
    from app.normalization import normalize_result

    p = normalize_result({
        "title": "Acme | LinkedIn",
        "url": "https://www.linkedin.com/company/acme",
        "text": "Acme builds software for sales teams.",
    })

    assert p.domain is None


def test_preserves_source_evidence():
    from app.normalization import normalize_result

    p = normalize_result({
        "title": "Acme | Company",
        "url": "https://acme.com/about",
        "text": "Acme uses HubSpot CRM.",
    })

    assert p.evidence[0].source_url == "https://acme.com/about"
    assert p.evidence[0].snippet == "Acme uses HubSpot CRM."