# Bulk Certificate Generator API

A REST API built with FastAPI that generates personalized PDF certificates for multiple recipients from a predefined certificate template. The system tracks generation jobs, records individual certificate statuses, handles recipient-level failures, and provides individual PDF and bulk ZIP downloads.

## Features

- **Bulk generation:** Submit multiple recipients in one API request.
- **PDF certificates:** Generate personalized certificates using ReportLab.
- **Job tracking:** Track job status, total recipients, successful generations, and failures.
- **Failure isolation:** A failed certificate does not stop processing for other recipients.
- **Individual downloads:** Retrieve a generated certificate as a PDF.
- **Bulk downloads:** Download available certificates for a job as a ZIP archive.
- **Input validation:** Validate required fields and reject invalid recipient data.
- **Interactive API documentation:** Explore and test endpoints using Swagger UI.
- **Automated tests:** Test API functionality and certificate generation with pytest.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server for running the API |
| SQLAlchemy | Database access and ORM |
| SQLite | Relational database |
| ReportLab | PDF certificate generation |
| Pydantic | Request validation and response schemas |
| pytest | Automated testing |
| HTTPX | HTTP client support for API tests |

## Project Structure

```text
bulk-certificate-generator/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   ├── certificate_service.py
│   │   └── job_service.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_certificate_service.py
├── generated/
├── requirements.txt
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.10 or later
- pip
- Git

## Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd bulk-certificate-generator
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the API

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

The SQLite database is initialized by the application. Generated PDF files are stored in the `generated/` directory.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check whether the API is running |
| POST | `/api/jobs` | Create a bulk certificate generation job |
| GET | `/api/jobs/{job_id}` | Retrieve job status and recipient results |
| GET | `/api/recipients/{recipient_id}/certificate` | Download an individual PDF |
| GET | `/api/jobs/{job_id}/certificates.zip` | Download successful certificates as a ZIP archive |

## Example: Create a Generation Job

Send a `POST` request to `/api/jobs` with the following JSON body:

```json
{
  "certificate_title": "Python Workshop",
  "organization": "ABC Institute",
  "recipients": [
    {
      "name": "Ananya Sharma",
      "email": "ananya@example.com"
    },
    {
      "name": "Rahul Verma",
      "email": "rahul@example.com"
    }
  ]
}
```

The response includes the job ID, status, recipient count, and success/failure totals.

## Job Status and Failure Handling

Each recipient is tracked separately. A generation job can have one of these statuses:

- `PENDING` — the job has not started.
- `PROCESSING` — certificates are being generated.
- `COMPLETED` — all certificates were generated successfully.
- `PARTIAL` — some certificates succeeded and others failed.
- `FAILED` — no certificates were generated successfully.

Because the current implementation processes the job synchronously, the creation request normally returns after processing finishes. The `PROCESSING` status is recorded internally, but it may not be observable through a separate status request while generation is underway.

## Download Certificates

- **Individual PDF:** Use the recipient ID returned by the job status endpoint.
- **ZIP archive:** Use the job ID to download all available successful certificates for that job.

A missing job, recipient, or unavailable certificate returns an appropriate HTTP error response.

## Database Design

The application uses two relational tables:

- **GenerationJob:** Stores the certificate title, organization, status, recipient totals, and creation timestamp.
- **Recipient:** Stores recipient information, individual generation status, output file path, and error details.

A generation job has a one-to-many relationship with its recipients.

## Running Tests

Run the automated test suite from the project root:

```bash
python -m pytest -v
```

The tests cover job creation, input validation, status tracking, certificate downloads, ZIP downloads, missing jobs, failure isolation, and PDF generation.

## Design Decisions

**FastAPI** provides request validation, REST endpoints, and automatically generated API documentation. **SQLite** provides a lightweight relational database without requiring a separate database server. **SQLAlchemy** maps database records to Python objects. **ReportLab** generates personalized PDF certificates from a shared template.

The current implementation uses synchronous processing to keep the solution straightforward and easy to run locally. Each recipient is processed independently, and the result is persisted in the database. A background task or queue could be introduced later for large workloads.

## Limitations and Future Improvements

- Add background processing for large batches.
- Use a production database such as PostgreSQL when required.
- Improve certificate layouts and support custom templates.
- Add authentication and authorization.
- Add structured logging and operational monitoring.
- Add pagination and configurable batch limits.
- Add stronger email validation and more comprehensive API tests.

## License

Add a license if you intend to distribute the project under specific reuse terms.
