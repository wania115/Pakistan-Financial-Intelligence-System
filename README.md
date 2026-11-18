# Pakistan Financial Intelligence System

A foundation for tracking Pakistan's macro-financial indicators, exploring historical data, and producing transparent economic analysis.

## Current foundation

- FastAPI application with versioned API endpoints
- SQLAlchemy data models for indicators, observations, and data sources
- PostgreSQL support, with SQLite as the local default
- Lightweight dashboard with an indicator catalog and observation trend view
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

## API

- `GET /health` — application health check
- `GET /api/v1/indicators` — indicator catalog
- `GET /api/v1/indicators/{code}/observations` — observations for an indicator; supports `start_date`, `end_date`, and `limit`

The initial catalog includes KIBOR, CPI inflation, USD/PKR, the SBP policy rate, and government-securities yields. Catalog entries are definitions, not published observations. Data ingestion and write endpoints are intentionally not enabled yet; source connectors and validation should be implemented before importing real observations.

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
  static/           Initial dashboard
  config.py         Environment-backed settings
  database.py       Engine, sessions, and initialization
  main.py           FastAPI application
```

## Development notes

- All observations should retain source and publication metadata as the ingestion pipeline is added.
- Forecasts must be clearly separated from observed data and include assumptions and uncertainty.
- Before production use, add database migrations, authentication/authorization where needed, automated tests, monitoring, and a reviewed source-data policy.
- The dashboard and API currently provide a read-only foundation; they do not represent investment advice.

## License

MIT. See [LICENSE](LICENSE).
