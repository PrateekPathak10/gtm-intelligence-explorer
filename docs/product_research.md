# Product Exploration: GTM Prospecting and Enrichment

## Purpose
The assignment asks for a time-boxed review of Orange Slice and Outmate's target workflow, followed by a working prototype. This is a short product note, not an exhaustive competitor teardown.

## Orange Slice: observed public workflow
Official product pages describe a natural-language lead-generation workflow: the user describes an ideal customer, the agent researches across sources and returns an enriched spreadsheet-like lead list. Its enrichment workflow describes uploading/pasting a list or describing the data needed, then filling firmographics, technographics and contact data. Its workflow page emphasizes checkpoints, retries, observability and control over provider/model keys.

Links:
- https://www.orangeslice.ai/product/lead-generation-agent
- https://www.orangeslice.ai/product/data-enrichment-agent
- https://www.orangeslice.ai/product/workflows

## Outmate: assignment and founder walkthrough
Based on the supplied assignment and Loom transcript:
- Outmate helps companies discover prospects, enrich data and automate outbound.
- The founder demonstrated a target of companies using HubSpot or Salesforce with 50–500 employees.
- Example fields include company name, domain, profile/description and employee count.
- The founder emphasized authentic information and noted Exa credits are available.
- The prototype should use Exa for research and investigate the "Mole Set" database/provider (public evidence suggests the name may be MoltSets; confirm with the founder).
- The requested scope is a rough but working prototype, not the complete platform.

## Feature comparison

| Capability | Orange Slice (public product pages) | Outmate target (assignment/transcript) | Prototype response |
|---|---|---|---|
| Natural-language ICP | Yes | Desired | Text prompt |
| Company discovery | Yes | Required | Exa search |
| Firmographics | Enriched results advertised | Desired | Populate only when sourced/provider-reported |
| Technology filters | ICP targeting advertised | HubSpot/Salesforce example | Query terms + evidence; not blindly verified |
| Growth signals | Hiring/news use cases advertised | Signals requested | Search evidence for hiring/funding/launches |
| Contact/decision-maker enrichment | Advertised | Desired where supported | MoltSets adapter only after API verification |
| Spreadsheet/table results | Yes | Rough interface accepted | Streamlit table |
| Evidence/source URLs | Research workflow implies multi-source research | Explicitly required | URLs/highlights preserved |
| API cost/credits | Product has usage model | Founder mentions credits | Defer actual accounting until metadata/pricing known |
| Workflow reliability | Checkpoints/retries/observability promoted | Error handling required | Timeouts, errors, provider status; future retries |

## Recommended first version
1. Input a company or ideal customer profile.
2. Search public web sources with Exa.
3. Normalize results into a stable schema.
4. Preserve evidence and sources.
5. Enrich through the confirmed provider when credentials and API schema are available.
6. Label missing/uncertain fields.
7. Export results and show provider errors transparently.

## Important trust rule
A search result containing a CRM vendor's name is not proof that the company uses that CRM. Similarly, a hiring article is not proof of a current opening. Each criterion should have a source and a status (source-backed, provider-reported, inferred, unavailable). Do not fabricate contact data, employee counts or intent.
