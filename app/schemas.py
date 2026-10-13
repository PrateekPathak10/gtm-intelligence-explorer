from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

EvidenceStatus = Literal["source-backed", "provider-reported", "inferred", "unavailable"]

class Evidence(BaseModel):
    claim: str
    source_url: str | None = None
    published_date: str | None = None
    status: EvidenceStatus = "source-backed"
    snippet: str | None = None

class Prospect(BaseModel):
    company_name: str
    domain: str | None = None
    description: str | None = None
    industry: str | None = None
    target_market: str | None = None
    employee_size: str | None = None
    technology_signals: list[str] = Field(default_factory=list)
    growth_signals: list[str] = Field(default_factory=list)
    potential_gtm_opportunity: str | None = None
    decision_makers: list[dict] = Field(default_factory=list)
    contact_information: list[dict] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low", "unavailable"] = "low"
    fit_status: str = "Needs review"
    provider_status: dict = Field(default_factory=dict)

class ResearchRequest(BaseModel):
    company_or_ideal_customer: str = Field(min_length=2, max_length=1000)
    research_objective: str = Field(default="Evaluate fit for a B2B GTM / outbound service.", max_length=1000)
    employee_min: int | None = Field(default=50, ge=1)
    employee_max: int | None = Field(default=500, ge=1)
    technologies: list[str] = Field(default_factory=list)
    growth_signals: list[str] = Field(default_factory=list)
    max_results: int = Field(default=8, ge=1, le=20)
