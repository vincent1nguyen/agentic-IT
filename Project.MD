# AI Ticket Assistant Project Notes

## Project Purpose

AI Ticket Assistant is a production-quality Chrome Extension and backend application for IT technicians who write ServiceNow tickets.

The application will help technicians turn rough troubleshooting notes into clean, structured ticket content. The technician remains responsible for reviewing the generated ticket before submitting it.

## Core Workflow

1. A technician types rough troubleshooting notes inside a ServiceNow ticket.
2. The Chrome Extension reads those notes.
3. The extension sends the notes to a FastAPI backend.
4. The backend sends the notes to an LLM.
5. The LLM summarizes the notes, selects the best ticket template, and generates structured ticket fields.
6. The extension fills the ServiceNow form.
7. The technician reviews everything before submitting.

## Long-Term Roadmap

### Phase 1

- FastAPI backend
- OpenAI integration
- Generate ticket summaries

### Phase 2

- Chrome Extension
- Auto-fill ServiceNow fields

### Phase 3

- PostgreSQL template storage
- Template selection

### Phase 4

- Learn from frequently used templates

### Phase 5

- Retrieval-Augmented Generation
- Vector database
- Previous ticket retrieval

## Tech Stack

### Frontend

- React
- TypeScript
- Chrome Extension Manifest V3

### Backend

- Python
- FastAPI

### Database

- PostgreSQL

### Testing

- Pytest
- Playwright

### Version Control

- Git

## Current Repository State

The repository started as a scaffold. The intended backend structure exists under `server/`.

Implemented so far:

- `server/pyproject.toml` defines the backend project metadata, Python version, FastAPI dependency, Uvicorn dependency, and Pytest configuration.
- `server/app/main.py` creates the FastAPI application instance.

Current structure:

```text
AI-Ticket-Assistant/
  README.md
  .gitignore
  .github/workflows/server-ci.yml
  server/
    pyproject.toml
    app/
      main.py
      api/routes.py
      core/config.py
      llm/openai.py
      models/ticket.py
      services/summarizer.py
    tests/
      test_health.py
      test_ticket.py
```

## Initial Architecture Direction

The backend will use a simple layered structure:

- `main.py` creates and configures the FastAPI application.
- `api/routes.py` defines HTTP endpoints.
- `models/ticket.py` defines typed request and response models.
- `services/summarizer.py` owns ticket summary business logic.
- `llm/openai.py` will isolate OpenAI-specific API calls.
- `core/config.py` will manage environment-based settings.
- `tests/` will contain backend tests.

This keeps HTTP routing, business logic, external LLM calls, and configuration separate. That separation makes the project easier to test and easier to extend later without rewriting the first version.

## Implementation Log

### Backend Foundation

#### `server/pyproject.toml`

Added the Python project configuration.

Purpose:

- Defines the backend package metadata.
- Requires Python 3.11 or newer.
- Adds `fastapi` for the web API framework.
- Adds `uvicorn[standard]` to run the FastAPI app locally.
- Adds development dependencies for `pytest` and `httpx`.
- Configures Pytest to find tests in `server/tests`.

Beginner note:

- `pyproject.toml` is similar to JavaScript's `package.json`.
- It describes the Python project and its dependencies.
- A Python lock file would be closer to JavaScript's `package-lock.json`, but this project does not have one yet.

#### `server/app/main.py`

Added the initial FastAPI app instance.

Current implementation:

```python
from fastapi import FastAPI

app = FastAPI(title="AI Ticket Assistant API")
```

Purpose:

- Creates the backend application object.
- Gives the API a human-readable title.
- Provides the object Uvicorn will load when running the server.

Beginner note:

- This is similar to creating an Express app with `const app = express()`.
- FastAPI defines the app and routes.
- Uvicorn is the local server that runs the FastAPI app and listens for HTTP requests.

## Development Rules For This Environment

Before writing code:

- Read the relevant files and understand the existing architecture.
- Search the codebase for existing implementations before writing new code.
- Reuse existing utilities, components, and patterns whenever possible.
- Make the smallest change necessary.
- Do not refactor unrelated code.
- Do not change APIs, folder structure, dependencies, or database schema unless explicitly requested.
- If a design decision is unclear, ask before implementing.
- Explain the current implementation.
- Identify what needs to change.
- List every file intended for modification.
- Wait for approval before editing.

Implementation standards:

- Write clean, maintainable, production-quality code.
- Prefer simple solutions over overengineered ones.
- Follow the current architecture and coding style.
- Keep commits focused on one feature.
- Use TypeScript or typed equivalents with explicit request, response, prop, and function types.
- Avoid implicit `any`.
- Pull repeated magic values into named constants.
- Avoid debug comments and scratch notes.
- Add comments only when they explain why something exists.

Project structure standards:

- Each component or function should have one clear job.
- Split files when they start mixing unrelated concerns.
- Extract repeated logic into a reusable function, hook, or module the first time it would be needed twice.
- Keep state minimal and localized.
- If a component needs more than three or four pieces of state, consider whether some state should become derived data, a custom hook, or context.

Testing and CI standards:

- Add at least one test per meaningful unit of logic.
- Use Pytest for backend tests.
- Use Playwright for frontend or extension workflow tests when applicable.
- Set up CI to run type checks, lint or format checks, and tests on pushes and pull requests.

Documentation standards:

- Keep `README.md` and project notes useful as real project documentation.
- Avoid stray scratch `.txt` files in the repo root.
- After each completed feature, summarize what was built, why it was built, and possible future improvements.

## Mentorship Notes

The project should be developed incrementally. Each major implementation should include an explanation of:

- what the code does,
- why the architecture was chosen,
- what tradeoffs exist,
- how the implementation supports future phases,
- and what a beginner should understand about the tool or pattern being used.

## Known Environment Notes

- `git status` is currently blocked because Git considers this repository an unsafe directory on this machine.
- To fix that later, Git may need this repository added as a safe directory.
