# Career_AI -- Backend

Career_AI is an AI-assisted resume analysis application. Its backend
provides user and resume management, authentication, document text
extraction, and AI-powered resume feedback.

The backend is built with **Python**, **FastAPI**, **SQLAlchemy**, and
**PostgreSQL**. It uses **Ollama** to run a locally hosted language
model for resume analysis.

## Features

- **JWT authentication** for protected API endpoints.
- **User management** and role-based access for users and
  administrators.
- **Resume management** with create, retrieve, update, and delete
  operations.
- **PDF and DOCX text extraction** so uploaded resumes can be
  analyzed.
- **AI-powered resume analysis** using an Ollama model.
- **Saved analysis results** stored in PostgreSQL so users can
  retrieve previous results without running the model again.
- **Resume snapshots and content hashes** stored with analyses to
  support tracking changes between resume versions.
- **Access control** to restrict resume access to its owner or an
  authorized administrator.

An analysis includes: - Summary - Strengths - Areas for improvement -
Detected skills - Missing or unclear information - Recommendations

## Technology stack

Technology Purpose

---

Python Backend programming language
FastAPI REST API framework
SQLAlchemy ORM and database access
PostgreSQL Relational database
PyJWT JWT token handling
pwdlib / Argon2 Password hashing
PyMuPDF PDF text extraction
python-docx DOCX text extraction
Ollama Local LLM runtime for resume analysis

## Project structure

The backend is organized into modules for API routes, database access,
authentication, configuration, data models, and services.

```text
career-ai-backend/
├── main.py
├── auth.py
├── config.py
├── database.py
├── models.py
├── schema.py
├── setup_admin.py
├── requirements.txt
├── .env.example
├── migrations/
│   └── 001_add_resume_snapshot_columns.sql
├── routers/
│   ├── resumes.py
│   └── users.py
└── services/
    ├── resume_analyzer.py
    ├── resume_text_extractor.py
    ├── resume_service.py
    ├── user_service.py
    ├── test_resume_analyzer.py
    └── test_text_extraction.py
```

\_

## Requirements

Before running the backend, install or prepare:

- Python (use a version compatible with the packages in
  `requirements.txt`)
- PostgreSQL
- Ollama
- The Ollama model configured for the application (the model used
  during development was `qwen3:4b`)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/marziyehbikas/career-ai.git
cd career-ai
```

Replace the repository URL with your actual GitHub repository URL.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, you can use Command Prompt
instead:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a
template:

```env
DATABASE_URL=your_database_url
SECRET_KEY=replace_with_a_long_random_secret
```

Use your own PostgreSQL connection string and a strong, private secret
key. Never commit your real `.env` file or publish credentials.

Check `config.py` and `.env.example` for the exact environment variables
required by the current version of the application. If additional
variables are defined there, add them to your local `.env` file.

### 5. Create the PostgreSQL database

Create a PostgreSQL database for the application, then set
`DATABASE_URL` in your `.env` file to point to it.

The application uses SQLAlchemy models for its database tables. The
`Base.metadata.create_all()` setup can create tables that do not yet
exist; it does not automatically add new columns to existing tables.

### 6. Apply the database migration

If you are using an existing database that was created before resume
snapshots were added, run the SQL in:

```text
migrations/001_add_resume_snapshot_columns.sql
```

The migration adds `resume_text_snapshot` and `content_hash` columns to
`resume_analyses`.

Back up your database before applying migrations. For a new database,
confirm the schema and migration requirements against the current models
before running the application.

### 7. Start Ollama

Install and start Ollama, then make sure the model configured in the
application is available. For the model used during development:

```bash
ollama pull qwen3:4b
```

Ollama must be running and accessible to the backend when you request an
AI resume analysis. The API can still retrieve previously saved analyses
from PostgreSQL without calling the model.

### 8. Run the FastAPI application

From the project root:

```bash
uvicorn main:app --reload
```

The `--reload` option is intended for local development, not production
deployment.

When the server starts, open the interactive API documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Resume analysis API

The resume analysis workflow has two main operations:

---

Method Endpoint Purpose

---

`POST` `/resumes/{resume_id}/analyze` Extracts the resume
text, requests an AI
analysis, and saves the
result and resume
snapshot in PostgreSQL.

`GET` `/resumes/{resume_id}/analysis` Retrieves the latest
saved analysis for the
resume. It reads from
PostgreSQL and does not
call Ollama.

---

These endpoints require the appropriate authentication and
authorization. A user can access their own resume; administrator access
is subject to the application's role and permission checks.

Use `/docs` to explore the complete API, request schemas, and other
available endpoints.

## Database and resume version tracking

Each saved resume analysis stores the generated analysis result along
with a snapshot of the extracted resume text and its SHA-256 content
hash.

- `resume_text_snapshot` preserves the text that was analyzed.
- `content_hash` provides a fingerprint of that extracted text.
  Identical text produces the same hash.
- The snapshot makes it possible to compare the actual resume content
  across analyses, rather than comparing only AI-generated feedback.

The hash is not encryption and should not be treated as a way to hide
resume content.

## Security notes

- Keep `.env` out of version control.
- Never commit database passwords, JWT secret keys, access tokens, or
  real user resumes.
- Use a strong, unique secret key outside development.
- Do not expose private resume files or personal information in a
  public repository.
- Configure CORS, HTTPS, logging, and production server settings
  appropriately before deployment.
- Treat uploaded documents and AI-generated output as untrusted input.

## Development checks

Check installed package compatibility with:

```bash
python -m pip check
```

Run the available service tests with the test runner used by the
project. If using `pytest`, install it as a development dependency if it
is not already installed, then run:

```bash
python -m pytest
```

## Related repository

The React frontend is maintained separately.

- Frontend repository: **Add your frontend GitHub repository URL
  here.**

## Project status

This project is under active development. Setup instructions and API
details may change as features are added.
