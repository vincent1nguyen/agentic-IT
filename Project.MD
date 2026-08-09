# AI IT Knowledge Assistant — Project Notes

## Project Purpose

AI IT Knowledge Assistant is a full-stack AI application designed to help IT technicians quickly find relevant troubleshooting information from a knowledge base.

Instead of manually searching through documentation, technicians can describe an IT issue in natural language. The application retrieves relevant knowledge-base documentation and uses an LLM to generate a concise troubleshooting response with supporting sources.

The project is intended to demonstrate practical software engineering and AI application development using Python, FastAPI, React, TypeScript, PostgreSQL, REST APIs, RAG, automated testing, Docker, and AWS.

The application should assist technicians rather than make decisions for them. Generated troubleshooting guidance should be reviewed by the technician before being acted upon.

---

# Core Workflow

1. A technician enters an IT support question or describes an issue.

2. The React frontend sends the question to the FastAPI backend through a REST API.

3. The backend processes the request and sends the query through the retrieval pipeline.

4. The retrieval system searches indexed knowledge-base documentation for information relevant to the technician's question.

5. Relevant document chunks are supplied to the LLM as context.

6. The LLM generates a troubleshooting response grounded in the retrieved documentation.

7. The backend returns a structured response containing:
   - troubleshooting guidance,
   - relevant supporting documentation,
   - citations or source references.

8. The React frontend displays the recommendation and its supporting sources to the technician.

Conceptually:

```text
Technician
    |
    v
React + TypeScript UI
    |
    | REST API
    v
FastAPI Backend
    |
    v
RAG Pipeline
    |
    +--------------------+
    |                    |
    v                    v
Vector Search      Knowledge Base
    |              Documentation
    +---------+----------+
              |
              v
       Relevant Context
              |
              v
          OpenAI LLM
              |
              v
 Troubleshooting Response
        + Citations
              |
              v
      React Frontend
```

---

# Primary Project Goals

The finished application should demonstrate several areas of software engineering.

## Full-Stack Development

Build a complete application using:

- React
- TypeScript
- Python
- FastAPI
- REST APIs
- PostgreSQL

The frontend and backend should remain separate applications communicating through clearly defined APIs.

## AI / LLM Development

Use an LLM to generate useful IT troubleshooting responses.

The system should demonstrate:

- OpenAI API integration
- prompt engineering
- structured LLM outputs
- context-aware generation
- response validation

## Retrieval-Augmented Generation

The LLM should not rely only on its existing knowledge.

Instead, the application should retrieve relevant documentation and provide that information to the model before generating its response.

The RAG system should eventually include:

- document ingestion,
- text chunking,
- embeddings,
- vector search,
- metadata,
- source retrieval,
- LangChain orchestration,
- cited responses.

## Software Engineering

The application should also demonstrate:

- typed data models,
- API design,
- separation of concerns,
- automated testing,
- unit testing,
- integration testing,
- debugging,
- Git version control,
- CI/CD,
- containerization,
- cloud deployment.

---

# Target User Experience

The technician should eventually be able to open the application and see a simple interface such as:

```text
--------------------------------------------------
AI IT Knowledge Assistant
--------------------------------------------------

Describe the issue:

[ User cannot connect to protected Wi-Fi.        ]
[ Authentication fails with an EAP-TLS error.   ]
[                                                  ]

                                      [ Ask AI ]

--------------------------------------------------
Recommended Troubleshooting
--------------------------------------------------

1. Verify that the device has a valid certificate.

2. Confirm the certificate has not expired.

3. Verify the device is using the correct
   authentication configuration.

4. If necessary, re-enroll the device certificate.

--------------------------------------------------
Sources
--------------------------------------------------

• Protected Wi-Fi Troubleshooting Guide
• Certificate Enrollment Documentation
--------------------------------------------------
```

The primary goal of the interface is speed and clarity.

Technicians should be able to describe an issue and quickly receive relevant documentation without manually searching through multiple knowledge-base pages.

---

# Knowledge Base

The portfolio version of this application should use public, synthetic, or otherwise authorized IT documentation.

Do not commit confidential, private, restricted, credential-bearing, or personally identifiable organizational data to the repository.

Example knowledge-base topics could include:

```text
knowledge_base/

wifi/
  protected-wifi.md
  certificate-errors.md

vpn/
  vpn-troubleshooting.md
  secure-client.md

authentication/
  password-reset.md
  mfa-troubleshooting.md

email/
  mailbox-access.md
  account-configuration.md

software/
  software-installation.md
```

These documents can simulate the type of internal documentation an IT support organization might maintain.

The architecture should allow a different authorized knowledge base to be indexed later without requiring major application changes.

---

# Tech Stack

## Frontend

- React
- TypeScript
- HTML
- CSS

Responsibilities:

- Accept technician questions.
- Send requests to the backend.
- Display AI-generated troubleshooting recommendations.
- Display supporting documentation and citations.
- Handle loading and error states.

---

## Backend

- Python
- FastAPI
- REST APIs
- Pydantic

Responsibilities:

- Receive technician questions.
- Validate request data.
- Coordinate retrieval and generation.
- Communicate with the LLM provider.
- Return structured API responses.
- Handle application errors.

---

## AI

- OpenAI API
- LangChain
- Prompt engineering
- Retrieval-Augmented Generation
- Embeddings
- Vector search

Responsibilities:

- Interpret technician questions.
- Retrieve relevant documentation.
- Generate troubleshooting recommendations using retrieved context.
- Produce structured responses.
- Reference supporting sources.

---

## Database

- PostgreSQL

PostgreSQL can initially store:

- document metadata,
- indexed knowledge-base information,
- application data.

A vector search solution can be introduced during the RAG phase.

One possible implementation is PostgreSQL with pgvector, but the exact vector storage implementation should be selected when the retrieval phase is built rather than prematurely coupling the project to one implementation.

---

## Testing

### Backend

- Pytest
- FastAPI TestClient / HTTPX
- Unit tests
- Integration tests

### Frontend

- Component or unit tests where useful
- Playwright for important user workflows

Important behaviors to test include:

- API validation,
- document retrieval,
- structured LLM responses,
- missing documentation,
- backend errors,
- frontend request handling,
- citation rendering.

---

## Infrastructure

- Docker
- Linux
- AWS
- GitHub Actions
- Git

Long-term infrastructure goals:

```text
GitHub
   |
   v
GitHub Actions
   |
   +--> Tests
   |
   +--> Build
   |
   v
Docker
   |
   v
AWS
```

The exact AWS architecture should be chosen when deployment work begins rather than adding unnecessary infrastructure during early development.

---

# Project Architecture

The backend should follow a simple layered architecture.

```text
server/

  app/

    main.py

    api/
      routes.py

    core/
      config.py

    models/
      ticket.py

    services/
      assistant.py
      retrieval.py

    llm/
      openai.py

    rag/
      ingestion.py
      embeddings.py
      retriever.py

  tests/
```

The structure may evolve as features are implemented.

Do not create files simply because they appear in this proposed architecture. Add files when the functionality actually requires them.

---

# Architecture Responsibilities

## `main.py`

Creates and configures the FastAPI application.

Responsibilities:

- create FastAPI app,
- register routers,
- configure application-level behavior.

---

## `api/`

Contains HTTP endpoints.

Example future endpoints:

```text
GET /health

POST /questions

POST /documents
```

Routes should primarily handle HTTP concerns.

Business logic should live in services rather than directly inside route handlers.

---

## `models/`

Contains typed request and response models.

Possible models include:

```text
QuestionRequest

QuestionResponse

SourceReference

RetrievedDocument
```

Pydantic should be used to validate API data and clearly define the contract between the frontend and backend.

---

## `services/`

Contains application business logic.

For example:

```text
assistant.py
```

could coordinate:

```text
question
   ↓
retrieval
   ↓
prompt construction
   ↓
LLM
   ↓
structured response
```

Services should not contain HTTP-specific behavior.

---

## `llm/`

Contains code specific to external LLM providers.

For example:

```text
llm/openai.py
```

should handle communication with the OpenAI API.

Keeping provider-specific code isolated prevents the rest of the application from depending directly on one external API implementation.

---

## `rag/`

Contains retrieval-specific functionality.

Eventually this may include:

```text
document ingestion
text chunking
embeddings
vector storage
similarity search
metadata filtering
source retrieval
```

These components should be introduced incrementally when the RAG phase begins.

---

## `core/`

Contains application configuration and shared infrastructure concerns.

For example:

```text
core/config.py
```

can manage environment variables such as:

```text
OPENAI_API_KEY

DATABASE_URL
```

Secrets must never be committed to Git.

---

# Development Roadmap

## Phase 1 — FastAPI Foundation

Goal:

Create a clean, tested backend foundation.

Features:

- FastAPI application
- API router
- `GET /health`
- Pydantic models
- Pytest setup
- environment configuration

Example:

```text
GET /health

Response:

{
  "status": "ok"
}
```

Purpose:

Establish the backend architecture and confirm the application can receive and return HTTP requests.

---

# Phase 2 — Basic AI Assistant

Goal:

Allow a technician to submit an IT question and receive an AI-generated response.

Initial flow:

```text
Question
   |
   v
POST /questions
   |
   v
FastAPI
   |
   v
OpenAI API
   |
   v
Structured Response
```

Example request:

```json
{
  "question": "A user cannot connect to Wi-Fi. What should I check?"
}
```

Possible response:

```json
{
  "answer": "Verify the network configuration and authentication settings.",
  "sources": []
}
```

At this phase, retrieval does not need to exist yet.

Purpose:

- Build OpenAI API integration.
- Practice prompt engineering.
- Establish structured AI responses.
- Separate LLM communication from application business logic.

---

# Phase 3 — Knowledge Base and RAG

Goal:

Ground AI responses in actual documentation.

This is a major milestone for the project.

Pipeline:

```text
Knowledge Base Documents
          |
          v
       Chunking
          |
          v
      Embeddings
          |
          v
     Vector Storage


Technician Question
          |
          v
      Embedding
          |
          v
    Similarity Search
          |
          v
 Relevant Document Chunks
          |
          v
      Prompt Context
          |
          v
         LLM
          |
          v
 Answer + Supporting Sources
```

Implementation should eventually include:

- document ingestion,
- document chunking,
- embeddings,
- vector storage,
- semantic search,
- retrieval,
- LangChain,
- citations.

The AI should be instructed to answer based on retrieved documentation and avoid inventing unsupported troubleshooting instructions.

---

# Phase 4 — React Technician Interface

Goal:

Build a usable frontend for technicians.

Technology:

- React
- TypeScript

Features:

- question input,
- submit button,
- loading state,
- error handling,
- troubleshooting response,
- supporting sources,
- citation display.

Flow:

```text
React
  |
  | POST /questions
  v
FastAPI
  |
  v
RAG + LLM
  |
  v
JSON Response
  |
  v
React UI
```

Purpose:

Turn the backend system into a complete full-stack application.

---

# Phase 5 — Testing and Reliability

Goal:

Make the system reliable and demonstrate production-oriented engineering practices.

Add:

- backend unit tests,
- API integration tests,
- retrieval tests,
- LLM response validation,
- frontend tests,
- Playwright workflow tests,
- error handling,
- logging.

Important scenarios:

- empty question,
- malformed request,
- LLM unavailable,
- database unavailable,
- no relevant documentation found,
- multiple relevant documents,
- invalid model response.

External APIs should be mocked where appropriate so tests remain deterministic and do not unnecessarily call paid services.

---

# Phase 6 — Docker, CI/CD, and AWS

Goal:

Deploy the application and automate testing/deployment workflows.

Add:

- Docker configuration,
- Linux deployment environment,
- GitHub Actions,
- automated tests on pushes and pull requests,
- AWS deployment.

Possible pipeline:

```text
Developer Push
      |
      v
    GitHub
      |
      v
GitHub Actions
      |
      +--> Run Tests
      |
      +--> Validate Build
      |
      v
 Docker Image
      |
      v
     AWS
```

The exact AWS service should be selected based on the application's requirements when deployment begins.

Do not add complex cloud infrastructure simply to increase the number of technologies used.

---

# Phase 7 — Optional ServiceNow Integration

The original AI Ticket Assistant concept can remain as a future extension of the project.

This phase is optional and should only begin after the core knowledge assistant works reliably.

Possible workflow:

```text
ServiceNow
    |
    v
Chrome Extension
    |
    v
FastAPI Backend
    |
    v
RAG + LLM
    |
    +--> Troubleshooting Assistance
    |
    +--> Ticket Summary
    |
    +--> Suggested Ticket Fields
```

Possible features:

- read technician troubleshooting notes,
- summarize completed troubleshooting,
- recommend relevant documentation,
- generate ticket descriptions,
- suggest ticket fields,
- assist with template selection,
- populate ServiceNow fields after technician approval.

The extension should assist with ticket creation rather than automatically submitting tickets.

---

# Resume Target

The finished project should provide legitimate technical evidence for resume bullets similar to the following.

### AI IT Knowledge Assistant

- Developed an AI assistant using Python, PostgreSQL, FastAPI, OpenAI API, and REST APIs to answer IT support questions, reducing manual knowledge-base search for technicians.

- Engineered a LangChain RAG pipeline using embeddings and semantic retrieval to identify relevant knowledge-base documentation and generate grounded troubleshooting responses with supporting citations.

- Constructed a React and TypeScript frontend for technicians to submit support questions and receive AI-generated troubleshooting recommendations with supporting documentation.

- Built a CI/CD pipeline using Docker, Linux, Git, GitHub Actions, and AWS to automate testing and deployment, improving release consistency and backend reliability.

These bullets describe the target finished application.

Do not claim a feature is complete until the corresponding functionality has actually been implemented and tested.

---

# Current Repository State

The repository originally began as the AI Ticket Assistant.

Current structure:

```text
AI-Ticket-Assistant/
  README.md
  .gitignore
  .github/
    workflows/
      server-ci.yml

  server/
    pyproject.toml

    app/
      main.py

      api/
        routes.py

      core/
        config.py

      llm/
        openai.py

      models/
        ticket.py

      services/
        summarizer.py

    tests/
      test_health.py
      test_ticket.py
```

The repository is still early enough that the project can transition to the AI IT Knowledge Assistant without significant rework.

Existing backend concepts such as:

- FastAPI,
- routing,
- configuration,
- LLM isolation,
- Pydantic models,
- testing,

remain relevant.

Some ticket-specific naming may eventually need to change as the implementation evolves.

Do not perform a large rename or refactor unless the existing names begin interfering with development.

---

# Current Implementation

## `server/pyproject.toml`

Defines the Python backend project.

Responsibilities:

- backend package metadata,
- Python version,
- FastAPI dependency,
- Uvicorn dependency,
- Pytest development dependency,
- HTTPX development dependency,
- Pytest configuration.

Beginner note:

`pyproject.toml` plays a role similar to `package.json` in a JavaScript project.

A lock file serves a role closer to `package-lock.json`.

---

## `server/app/main.py`

Creates the FastAPI application instance.

Current implementation:

```python
from fastapi import FastAPI

app = FastAPI(title="AI Ticket Assistant API")
```

This name can eventually be updated to:

```python
app = FastAPI(title="AI IT Knowledge Assistant API")
```

but avoid unrelated changes while implementing other features.

Beginner note:

This is similar to:

```javascript
const app = express();
```

in an Express application.

FastAPI creates the application.

Uvicorn runs it and listens for incoming HTTP requests.

---

# Next Planned Step

Continue building the backend foundation.

Implement:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

Implementation order:

```text
server/app/api/routes.py
        ↓
server/app/main.py
        ↓
server/tests/test_health.py
```

The purpose of this endpoint is to:

- verify the backend is running,
- establish the routing pattern,
- create the first API test,
- confirm the FastAPI/Pytest development environment works.

After the backend foundation is working, begin the basic `/questions` API before implementing RAG.

Do not start with LangChain, embeddings, PostgreSQL vector search, React, or AWS.

Build the system incrementally.

---

# Development Rules For This Environment

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

---

# Implementation Standards

- Write clean, maintainable, production-quality code.
- Prefer simple solutions over overengineered ones.
- Follow the current architecture and coding style.
- Keep commits focused on one feature.
- Use explicit types for requests, responses, props, and important functions.
- Avoid implicit `any` in TypeScript.
- Use Pydantic models for Python API boundaries.
- Pull repeated magic values into named constants.
- Avoid debug comments and scratch notes.
- Add comments only when they explain why something exists.
- Keep secrets in environment variables.
- Never commit API keys.

---

# Project Structure Standards

- Each component, function, class, or module should have one clear responsibility.
- Split files when they begin mixing unrelated concerns.
- Extract repeated logic when it genuinely becomes reusable.
- Avoid creating abstractions before they are necessary.
- Keep frontend state minimal and localized.
- Keep HTTP concerns out of business logic.
- Keep external API implementation details isolated from services.
- Keep retrieval logic separate from LLM generation where practical.

---

# Testing and CI Standards

- Add at least one test per meaningful unit of logic.
- Use Pytest for backend tests.
- Use Playwright for important frontend workflows when applicable.
- Mock external LLM calls in automated tests where appropriate.
- Avoid tests that depend on nondeterministic LLM responses.
- Run tests automatically through CI.
- Add formatting, linting, or type checks when those tools become part of the project.

---

# Documentation Standards

Keep:

```text
README.md
Project.md
```

useful as real project documentation.

As the project grows, documentation may include:

```text
docs/
  architecture.md
  rag.md
  api.md
  deployment.md
```

Do not create documentation files until there is enough information to justify them.

After each completed feature, document:

- what was built,
- why it was built,
- important architectural decisions,
- tests added,
- possible future improvements.

---

# Mentorship Rules

This project should be developed incrementally as both a portfolio project and a learning experience.

For each meaningful implementation:

1. Explain what we are about to build.
2. Explain why it belongs in the architecture.
3. Explain important technologies or patterns involved.
4. Identify the files that will change.
5. Wait for approval before editing.
6. Implement the smallest useful version.
7. Run or describe relevant tests.
8. Explain the completed code.
9. Explain what the developer should understand from the implementation.
10. Identify the logical next step.

Do not simply generate large amounts of code without explanation.

When introducing a new technology such as:

- FastAPI,
- Pydantic,
- PostgreSQL,
- embeddings,
- vector search,
- LangChain,
- Docker,
- GitHub Actions,
- AWS,

explain what problem the technology solves and why it is being introduced at that point in the project.

---

# Guiding Principle

Build the simplest working version first.

The progression should generally be:

```text
FastAPI
   ↓
REST API
   ↓
OpenAI
   ↓
Structured AI Responses
   ↓
Knowledge Base
   ↓
Retrieval
   ↓
RAG
   ↓
PostgreSQL / Vector Search
   ↓
React + TypeScript
   ↓
Testing and Reliability
   ↓
Docker
   ↓
CI/CD
   ↓
AWS
   ↓
Optional ServiceNow Integration
```

Every new technology should solve a real problem in the application rather than being added only for resume keywords.
