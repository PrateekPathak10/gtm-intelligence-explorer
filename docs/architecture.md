# Architecture and Provider Notes

## Components
- `app/main.py`: Streamlit UI and CSV/JSON downloads.
- `app/api.py`: optional FastAPI endpoint.
- `app/providers/exa_provider.py`: Exa SDK wrapper and error translation.
- `app/providers/moltsets_adapter.py`: enrichment adapter boundary; disabled until endpoint schema is confirmed.
- `app/normalization.py`: source normalization and deduplication.
- `app/schemas.py`: typed request, prospect and evidence models.
- `app/research.py`: query construction and provider orchestration.

## Error handling
- Missing Exa key: explicit configuration message.
- Exa rate limit/timeouts: translated to user-readable errors.
- Empty search: empty-state warning.
- MoltSets unconfigured: provider status is marked `not_configured`.
- Provider errors are recorded per prospect instead of fabricating values.

## Security
- API keys are read from environment variables on the server.
- `.env` is ignored by Git.
- Do not put secrets in Streamlit widgets, client-side code or screenshots.
- Use only authorized enrichment endpoints and follow provider terms.

## Known limitations
- Search result-to-company entity resolution is basic.
- ICP filters influence the query but are not yet independently verified.
- No real usage/cost calculation until provider usage data is confirmed.
- MoltSets live endpoint is not enabled pending confirmation.
