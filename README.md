# GTM Intelligence Explorer

### Evidence-Backed Company Discovery & Enrichment Prototype

**Built as part of the Outmate AI Engineer Intern assignment**

GTM Intelligence Explorer is a research and prospect-discovery prototype designed to help B2B teams identify potential customers from public information. It uses Exa search to retrieve relevant web sources, normalizes the results into structured company records, extracts supported signals, and presents the findings in an interactive Streamlit interface.

The core principle is simple: **use evidence to support prospecting decisions, and never present an unverified assumption as a confirmed company fact.**

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Using the Application](#using-the-application)
- [API Usage](#api-usage)
- [Data Quality and Error Handling](#data-quality-and-error-handling)
- [Testing](#testing)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Security](#security)

## Problem Statement

B2B sales and growth teams often spend considerable time researching companies, identifying relevant prospects, collecting supporting evidence, and preparing data for outbound workflows.

A useful prospecting system should help answer questions such as:

- Which companies might fit our ideal customer profile (ICP)?
- What public evidence supports their relevance?
- Are there signals of technology adoption, hiring, funding, or expansion?
- Which important fields remain unknown and require further research?
- Can the results be exported into a downstream sales or enrichment workflow?

The challenge is not simply finding search results. It is converting unstructured information into useful, traceable, and appropriately qualified prospect records.

## Solution Overview

GTM Intelligence Explorer provides an interactive workflow for researching potential B2B prospects.

Users describe a target company or ideal customer profile, define employee-count boundaries, select technology and growth signals, and specify a research objective.

The application then:

1. Builds a search query from the user's criteria.
2. Uses the Exa API to retrieve public web results and available highlights.
3. Normalizes retrieved results into structured prospect records.
4. Extracts supported company attributes and available evidence.
5. Applies preliminary qualification logic and labels records requiring review.
6. Attempts enrichment through a provider adapter when configured.
7. Displays results and source evidence in Streamlit.
8. Allows users to export the results as JSON or CSV.

The prototype is designed to be extensible so that additional research and enrichment providers can be integrated without coupling the entire application to one provider.

## Key Features

### 1. ICP-Based Prospect Research

Users can define their target audience using:

- A company name or ideal customer description
- Minimum and maximum employee counts
- Technology signals such as HubSpot and Salesforce
- Growth signals such as sales hiring, funding, product launches, and expansion
- A custom research objective
- A configurable maximum number of search results

### 2. Exa Search Integration

The research provider uses the Exa Python SDK to retrieve relevant web results and available text highlights.

The application captures supported information such as:

- Result title
- Source URL
- Available publication date
- Available author
- Retrieved text highlights

The Exa API key is loaded from environment configuration rather than hardcoded into application code.

### 3. Structured Company Records

Research results are normalized into structured records with fields including:

- Company name
- Domain
- Description or available evidence
- Industry
- Employee-size estimate or reported count
- Technology signals
- Growth signals
- Potential GTM opportunity
- Decision-makers
- Contact information
- Source evidence
- Confidence and qualification status
- Provider status

Fields that cannot be established reliably should remain unavailable or unverified rather than being fabricated.

### 4. Evidence-First Qualification

Search results are treated as candidate prospects, not automatically qualified leads.

The qualification logic considers available employee-size information and requested ICP criteria. It distinguishes potential matches from records requiring further verification.

A company appearing in a search result does not, by itself, prove that the company meets every ICP requirement.

### 5. Enrichment Provider Adapter

The project includes a MoltSets enrichment adapter intended to separate provider-specific functionality from the core research workflow.

**Current status:** Live MoltSets enrichment is not configured in this prototype because the required provider configuration has not been established. The application reports this limitation rather than manufacturing enrichment results.

The adapter can be connected to the provider's confirmed API once its authentication method, endpoint, request schema, response schema, and access permissions are available.

### 6. Interactive Results and Export

The Streamlit interface presents research results in a table and provides expandable evidence sections for individual prospects.

Users can download the generated records as:

- JSON for structured processing and integrations
- CSV for spreadsheet review and downstream workflows

### 7. Automated Tests

The project includes tests for normalization, domain extraction, deduplication, missing-field handling, employee-size extraction, technology-signal handling, and query construction.

The test suite is intended to protect important data-quality rules as the prototype evolves.

## How It Works

```text
User Input / ICP
       |
       v
Research Request Validation
       |
       v
Search Query Construction
       |
       v
Exa API
       |
       v
Search Results and Highlights
       |
       v
Candidate Filtering and Deduplication
       |
       v
Company Data Normalization
       |
       v
Evidence and Qualification Logic
       |
       v
Optional Enrichment Adapter
       |
       v
Streamlit Results Interface
       |
       +------> JSON Export
       |
       +------> CSV Export
```

The research, normalization, and enrichment stages are separated to make the system easier to test, debug, and extend.

## Technology Stack

| Technology                                | Purpose                                       |
| ----------------------------------------- | --------------------------------------------- |
| Python                                    | Core application and processing logic         |
| Streamlit                                 | Interactive user interface                    |
| Exa Python SDK                            | Public web research and search highlights     |
| Pydantic                                  | Structured data models and request validation |
| Pandas                                    | Tabular results and CSV export                |
| FastAPI                                   | Optional REST API interface                   |
| Pytest                                    | Automated testing                             |
| python-dotenv / environment configuration | Local configuration and API credentials       |
| Git and GitHub                            | Version control and project delivery          |

## Architecture

The application is organized into modular components.

```text
gtm-intelligence-explorer/
├── app/
│   ├── main.py
│   ├── api.py
│   ├── config.py
│   ├── schemas.py
│   ├── research.py
│   ├── normalization.py
│   └── providers/
│       ├── exa_provider.py
│       └── moltsets_adapter.py
├── tests/
│   ├── test_normalization.py
│   └── test_research.py
├── docs/
│   ├── architecture.md
│   └── product_research.md
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Component Responsibilities

**`app/main.py`**
Provides the Streamlit interface, research controls, results table, evidence views, and download options.

**`app/api.py`**
Provides the optional FastAPI interface, including health and research endpoints.

**`app/config.py`**
Loads application settings and environment variables.

**`app/schemas.py`**
Defines structured request, prospect, and evidence models.

**`app/research.py`**
Constructs search queries, coordinates providers, filters candidate results, deduplicates records, and applies qualification logic.

**`app/normalization.py`**
Normalizes retrieved results, extracts supported fields, and applies data-quality rules.

**`app/providers/exa_provider.py`**
Encapsulates Exa client initialization, search requests, result handling, and provider error reporting.

**`app/providers/moltsets_adapter.py`**
Encapsulates optional enrichment-provider integration.

**`tests/**`**
Contains automated tests for important application behavior.

## Getting Started

### Prerequisites

- Python 3.11 or a compatible Python version supported by the project dependencies
- pip
- An Exa API key
- Git, if cloning the repository

### 1. Clone the repository

```bash
git clone https://github.com/PrateekPathak10/gtm-intelligence-explorer.git
cd gtm-intelligence-explorer
```

### 2. Create a virtual environment

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

```bash
cp .env.example .env
```

Edit `.env` and provide your own Exa API key:

```dotenv
EXA_API_KEY=your_exa_api_key
MOLTSETS_API_KEY=
MOLTSETS_BASE_URL=
MOLTSETS_SEARCH_COMPANIES_PATH=
REQUEST_TIMEOUT_SECONDS=25
MAX_SEARCH_RESULTS=10
```

Do not commit the `.env` file or share API credentials publicly.

MoltSets settings should only be populated after the actual API endpoint and request format have been confirmed.

### 5. Run the application

```bash
streamlit run app/main.py
```

Streamlit will display a local URL, usually:

`http://localhost:8501`

Open that URL in your browser.

### 6. Run the tests

```bash
python -m pytest -q
```

To check Python compilation:

```bash
python -m compileall app
```

## Configuration

| Variable                         | Purpose                                 |
| -------------------------------- | --------------------------------------- |
| `EXA_API_KEY`                    | Exa API authentication                  |
| `MOLTSETS_API_KEY`               | Optional enrichment-provider credential |
| `MOLTSETS_BASE_URL`              | Confirmed enrichment API base URL       |
| `MOLTSETS_SEARCH_COMPANIES_PATH` | Confirmed enrichment endpoint path      |
| `REQUEST_TIMEOUT_SECONDS`        | Request timeout configuration           |
| `MAX_SEARCH_RESULTS`             | Maximum search-result limit             |

The exact availability and behavior of provider features depend on the relevant account, API access, and provider response.

## Using the Application

1. Start the Streamlit application.
2. Enter a company name or describe the ideal customer profile.
3. Set the desired employee-count range.
4. Select technology and growth signals.
5. Enter the research objective.
6. Choose the maximum number of research results.
7. Click **Research prospects**.
8. Review the company records and available source evidence.
9. Check the qualification status and any unavailable fields.
10. Export the results as JSON or CSV.

### Example Research Input

**Ideal customer profile:**
B2B SaaS companies using HubSpot or Salesforce, with 50–500 employees and signs of sales-team expansion.

**Research objective:**
Evaluate whether a company could benefit from an AI-powered B2B GTM and outbound prospecting service.

This is an example input, not a claim that every returned company satisfies the specified criteria.

## API Usage

The optional FastAPI service exposes the following endpoints when `app/api.py` is run through Uvicorn.

Start the API:

```bash
uvicorn app.api:app --reload
```

### Health Check

```http
GET /health
```

Use this endpoint to check whether the API process is responding.

### Research Endpoint

```http
POST /research
Content-Type: application/json
```

Example request:

```json
{
  "company_or_ideal_customer": "B2B SaaS companies using HubSpot or Salesforce",
  "research_objective": "Identify potential prospects for an outbound GTM service",
  "employee_min": 50,
  "employee_max": 500,
  "technologies": ["HubSpot", "Salesforce"],
  "growth_signals": ["Sales hiring"],
  "max_results": 5
}
```

The request schema validates supported fields and configured limits. Actual results depend on the search provider's response and available evidence.

The precise response structure is defined by the application's Pydantic models and API implementation.

## Data Quality and Error Handling

A prospecting tool should help users make better decisions without overstating what the available data proves.

This prototype follows several principles:

- **Source traceability:** Retain source URLs and available supporting text.
- **No fabricated enrichment:** Do not invent employee counts, contacts, decision-makers, technology usage, or buying intent.
- **Explicit uncertainty:** Mark missing or unverified information appropriately.
- **Deduplication:** Avoid returning repeated prospects with the same normalized domain.
- **Qualification transparency:** A preliminary fit is not equivalent to a verified sales-qualified lead.
- **Provider isolation:** Report provider failures rather than silently replacing failed requests with fabricated records.
- **Defensive error handling:** Handle missing credentials, rate limits, timeouts, and unexpected provider errors where implemented.

### Evidence Statuses

| Status                   | Meaning                                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| Source-backed            | The claim is supported by retrieved source content; the original source should still be reviewed |
| Provider-reported        | An authorized enrichment provider returned the information                                       |
| Inferred                 | A reasoned interpretation that is not a confirmed fact                                           |
| Unavailable / Unverified | The information could not be established reliably                                                |

Search snippets can be incomplete or misleading. Source-backed does not automatically mean independently verified.

## Testing

The project includes automated tests covering key parts of the research pipeline.

Run:

```bash
python -m pytest -q
```

The current development test run completed with **15 tests passing**. This result describes the test suite at that point in development; it does not guarantee the correctness of every live search result or external API integration.

The following checks are also useful before submission:

```bash
python -m compileall app
git status --short
```

For a final smoke test, run a live research query, open several source URLs, inspect the downloaded CSV and JSON, and verify that the `.env` file is excluded from version control.

## Current Limitations

This is a working prototype, not a production-ready sales intelligence platform.

1. **Enrichment integration:** MoltSets is not configured for live enrichment. Its actual supported fields and behavior must be confirmed before integration.
2. **Search relevance:** Exa may return articles, third-party profiles, or pages that mention a company without representing the company itself.
3. **Employee counts:** Counts and ranges extracted from text may be outdated, approximate, or refer to a different organization. Original sources must be checked.
4. **Technology signals:** A mention of HubSpot or Salesforce does not prove that a company uses that technology.
5. **Growth signals:** A general hiring or funding mention does not necessarily establish a current sales expansion opportunity.
6. **Contact information:** Verified decision-makers and contact details are not guaranteed when the available sources do not provide them.
7. **Qualification:** Fit status is preliminary and depends on the evidence available to the application.
8. **External dependencies:** Live research depends on API credentials, provider availability, network connectivity, and account limits.

These limitations are surfaced rather than hidden so the prototype remains transparent about the quality of its output.

## Future Improvements

Potential next steps include:

- Integrate the confirmed enrichment API and validate its response schema.
- Add company-level domain verification and stronger entity resolution.
- Use targeted follow-up searches to verify employee counts and technology adoption.
- Improve the distinction between a company's own website and third-party articles.
- Add evidence snippets and source-level explanations for every qualification decision.
- Implement more precise confidence scoring based on evidence quality and source agreement.
- Add caching, retry policies, request logging, and usage tracking.
- Add provider-level integration tests and more edge-case tests.
- Add asynchronous processing for larger research jobs.
- Support exporting validated records into CRM systems.
- Evaluate results against a manually reviewed benchmark dataset.

## Security

- Store API keys in environment variables.
- Keep `.env` out of Git.
- Do not include credentials in screenshots, logs, source code, or the public README.
- Use only API endpoints and credentials that you are authorized to access.
- Review the repository contents before pushing changes to GitHub.

## Project Status

The prototype demonstrates an end-to-end research workflow with Exa, structured company records, evidence presentation, preliminary qualification, and CSV/JSON export.

The optional MoltSets enrichment stage remains unconfigured and is explicitly reported as such.

**Author:** Prateek Pathak
**Repository:** [GTM Intelligence Explorer](https://github.com/PrateekPathak10/gtm-intelligence-explorer)

