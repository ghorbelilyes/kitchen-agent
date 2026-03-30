# Kitchen Validator Phase 3

This Phase 3 scaffold is designed to run as three simple local services:

- Backend: Java 17 + Maven 3.6+
- Frontend: plain `index.html` served by any basic HTTP server
- Agent: Python 3.10+ with FastAPI/Uvicorn

## Required Versions

### Backend

- Java: 17
- Maven: 3.6 or newer

Run it with:

```bash
cd backend
mvn spring-boot:run
```

Note: this scaffold does not include Maven wrapper scripts, so Maven must be installed on your machine.

### Frontend

- No Node.js or frontend framework is required.
- The UI is a single plain HTML file that uses vanilla JavaScript and the native `fetch()` API.
- Any static HTTP server is fine.

Recommended local command:

```bash
cd frontend
python3 -m http.server 4200
```

### Agent

- Python: 3.10 or higher
- pip: standard `pip`

Install and run:

```bash
cd agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Current Python dependencies:

- `fastapi`
- `uvicorn`
- `pydantic`
- `loguru`
- `python-multipart`

## Recommended Startup Order

1. Start the FastAPI agent on port `8000`
2. Start the Spring Boot backend on port `8080`
3. Serve `frontend/index.html` on port `4200`

Then open:

```text
http://localhost:4200
```
