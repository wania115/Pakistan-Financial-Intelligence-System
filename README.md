# Pakistan Financial Intelligence System

A foundation for tracking Pakistan's macro-financial indicators, exploring historical data, and producing transparent economic analysis.

## Current foundation

- FastAPI application with versioned API endpoints
- SQLAlchemy data models for indicators, observations, company reports, and data sources
- PostgreSQL support, with SQLite as the local default
- Lightweight dashboard with an indicator catalog and observation trend view
- PSX company-report PDF ingestion foundation for annual and half-yearly reports
- Docker Compose development environment
- No fabricated observations: the dashboard displays an empty state until verified data is loaded

## Quick start (local)

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

Open <http://localhost:8000> for the dashboard and <http://localhost:8000/docs> for interactive API documentation. The local default database is `./pfis.db`.

## Quick start (Docker)

```bash
docker compose up --build
```

The dashboard is available at <http://localhost:8000>. Docker Compose runs the API and PostgreSQL; data is stored in a named volume.

## PSX company reports

The initial connector accepts a direct PDF URL copied from the official PSX Financials portal. It is an on-demand CLI, not an unrestricted crawler: PSX domains are allowlisted, HTTPS is required, redirects are checked, and PDF size/page limits are enforced. The connector extracts selectable PDF text and identifies likely balance-sheet, income-statement, and cash-flow sections. Scanned image-only PDFs currently need OCR, which is not enabled.

```bash
PYTHONPATH=backend python -m app.tools.ingest_psx_report \
  --symbol EXAMPLE --company "Example Limited" --period annual \
  --fiscal-year 2025 --url "https://financials.psx.com.pk/path/report.pdf"
```

Use `--period half_yearly` for a half-yearly report. This connector does not guess report URLs or crawl the whole site; select the company/report from the PSX portal and pass the resulting PDF link. Source documents should be accessed in line with PSX terms and any applicable licensing.

### Report API

- `GET /api/v1/company-reports` — list reports; optional `symbol`, `report_type`, `fiscal_year`, and `limit` filters
- `GET /api/v1/company-reports/{report_id}/analysis` — report metadata, reviewed figures, and ratios

PDF text and statement excerpts are retained for analysis. Automated extraction of line-item figures from diverse PDF layouts is not considered reliable without review. Ratio calculations use only explicitly reviewed financial data; missing values return `null` rather than inferred numbers. Standard ratio keys are `current_assets`, `current_liabilities`, `total_debt`, `total_equity`, `gross_profit`, `revenue`, `net_income`, `total_assets`, and `operating_cash_flow`.

The PSX portal is available at <https://financials.psx.com.pk/>. No public, documented bulk API is assumed by this implementation.

## Existing indicator API

- `GET /health` — application health check
- `GET /api/v1/indicators` — indicator catalog
- `GET /api/v1/indicators/{code}/observations` — observations for an indicator; supports `start_date`, `end_date`, and `limit`

The initial catalog includes KIBOR, CPI inflation, USD/PKR, the SBP policy rate, and government-securities yields. Catalog entries are definitions, not published observations.

## Configuration

Settings are read from environment variables (or a `.env` file):

| Variable | Default | Description |
|---|---|---|
| `PFIS_DATABASE_URL` | `sqlite:///./pfis.db` | SQLAlchemy database URL |
| `PFIS_APP_NAME` | `Pakistan Financial Intelligence System` | Application title |
| `PFIS_DEBUG` | `false` | Enable development debug mode |

## Project layout

```text
backend/app/
  api/routes/       Versioned API routes
  models/           SQLAlchemy database models
  schemas/          Pydantic API schemas
  services/         Analysis and ingestion services (planned)
  static/           Initial dashboard
  tools/            On-demand report ingestion CLI
  config.py         Environment-backed settings
  database.py       Engine, sessions, and initialization
  main.py           FastAPI application
```

## Development notes

- Preserve report source URLs, period metadata, and review status.
- Forecasts and extracted data must remain clearly separated from verified observations and include assumptions.
- Before production use, add database migrations, a review workflow, authentication/authorization, automated tests, monitoring, and a reviewed source-data policy.
- The current service does not provide investment advice.

## License

MIT. See [LICENSE](LICENSE).
