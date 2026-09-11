# Current Development Session

Date: September 10, 2026

## Current Goal

Evolve the project from a question-answering knowledge assistant into an agentic IT support assistant that can retrieve internal context, choose an appropriate tool, and safely perform approved support actions.

The immediate milestone is a small VPN knowledge-data foundation using user-supplied public or authorized material. Start with one VPN document; ticket history and additional scenarios are deferred. All data must be public, fictional, sanitized, or explicitly authorized.

## Current State

- The project has a working FastAPI application in `main.py`.
- `GET /health` returns `{ "status": "ok" }`.
- `POST /questions` validates nonblank input and generates an answer through the OpenAI provider in `llm.py`.
- The response contract is currently `{ "answer": string, "sources": [] }`.
- Provider configuration and failures are mapped to safe HTTP errors.
- Automated tests use test doubles and do not make paid OpenAI API requests.
- `knowledge.py` defines Pydantic `Document`, `Ticket`, and `SearchResult` models with nonblank text validation, source references, sensitivity, and synthetic-data labels.
- `data/seed.json` contains one public UCSD VPN document and an empty tickets list. It preserves the supplied PDF's extracted article text, including platform instructions and tunnel-group rules; screenshots are not searchable text.
- Original PDF: `mockdata/IT Services - Configure VPN Client on your Computer, Tablet, or Phone.pdf`.
- Source: https://support.ucsd.edu/services?id=kb_article_view&sysparm_article=KB0020109. The record is marked `public` and `is_synthetic: false`; timestamps describe the local record, not UCSD publication dates.
- `knowledge_repository.py` validates the entire document batch before storage, creates the SQLite `documents` table, and inserts or updates by ID. It rejects duplicate seed IDs and nonempty ticket data; ticket storage is not implemented.
- Ran `.venv\Scripts\python.exe knowledge_repository.py` successfully: one document loaded into `data/knowledge.db`. The generated database and its sidecar files are excluded in `.gitignore`.
- Foundation testing is complete: `.venv\Scripts\python.exe -m pytest -q` passed all 47 tests (40 new foundation cases and 7 existing API/provider cases), without paid model calls. Tests use temporary databases and fictional fixtures; the seed dataset is unchanged. Coverage includes repeatable loading, updates, retained records, batch validation, transaction rollback, filtering, ranking, citations, empty results, and input validation.
- `search_documents` in `knowledge_repository.py` now reads SQLite in read-only mode, filters by permitted sensitivity (public by default) and optional service, and ranks distinct keyword matches with title/tag/content weights of 3/2/1. Ties use document ID. Results include source references, sensitivity, synthetic labels, and an excerpt selected from overlapping 160-word passages. Blank inputs and invalid limits are rejected; no matches return an empty list.
- The real VPN tunnel-group regression passes: the excerpt includes campus-only/all-traffic routing rules, secure-connect options, and NAC requirements, with the original source reference. API grounding, tool calling, action approval, and audit logging are not implemented. The existing API is unchanged.
- Refactored search into `_validate_search_inputs`, `_read_documents`, and `_score_document` helpers at the user's request. SQL construction, connection handling, and row conversion stay together in `_read_documents`; `search_documents` coordinates retrieval, result construction, and sorting. Foundation tests now exercise this implementation.
- The first test run found a test expectation comparing equivalent UTC timestamp strings (`Z` versus `+00:00`); corrected the test to compare datetime values. No production code fixes were needed. The suite emits one Starlette/httpx deprecation warning.

## Working Agreement

- Choose the smallest simple implementation; use SQLite and deterministic keyword/tag search without embeddings or new frameworks.
- Before each implementation step, explain the proposed code/files and how they support the goal, then wait for approval.
- After implementing an approved step, pause so the user can understand it before moving forward.
- The user supplies seed information. Do not invent additional documents or tickets without agreement; current scope is VPN only.
- Testing was deferred until the end of the data-foundation implementation; that testing step is now approved and complete. Continue testing subsequent changes before API integration.
- The user reviewed search, approved the helper refactor, and approved foundation testing. Pause to review the passing results before proposing the next implementation step.

## New Product Direction

The assistant should support two related modes:

1. **Answer mode**: retrieve authorized internal information and produce a grounded answer with citations.
2. **Action mode**: determine whether an available tool can help, explain the proposed action, obtain approval when required, execute it, and report the result.

The assistant must never treat generated text as authorization. Tool permissions, input validation, approval policy, and audit records must be enforced in application code.

## Proposed Agent Loop

```text
User request
    |
    v
Retrieve relevant KB, internal docs, and ticket history
    |
    v
Model chooses: answer, ask for clarification, or propose a tool
    |
    v
Application validates tool, arguments, permission, and approval policy
    |
    v
Execute approved tool through a controlled adapter
    |
    v
Return outcome, supporting sources, and audit reference
```

## Phased Plan

### Phase 1 - VPN Data Foundation

- [x] Define typed document, ticket, and search-result models.
- [x] Prepare one user-supplied public VPN article as seed data.
- [x] Create the SQLite document schema and load the first document.
- [x] Implement and verify insert-or-update seed loading by document ID.
- [x] Add deterministic document search functions.
- [x] Test repository loading and document search.
- [x] Add provenance and sensitivity metadata to the current record.
- [ ] Add ticket fixtures and SQLite ticket storage when the user expands scope.

Suggested initial entities:

- `documents`: title, content, document type, product/service, tags, source reference, sensitivity, created/updated dates.
- `tickets`: synthetic ticket ID, summary, symptoms, resolution, category, status, timestamps, and related document references.
- `document_chunks`: optional derived records added when retrieval requires chunk-level search.

### Phase 2 - Grounded Answers

- [ ] Retrieve relevant records for a support question.
- [ ] Pass only selected authorized context to the model.
- [ ] Return citations in the existing `sources` field.
- [ ] Define behavior for weak or missing evidence.
- [ ] Test retrieval and grounding independently from the model.

### Phase 3 - Tool Framework

- [ ] Define a typed tool interface and registry.
- [ ] Begin with read-only mock tools, such as looking up a user/device or searching tickets.
- [ ] Add simulated write tools, such as creating a draft ticket or requesting a password reset.
- [ ] Validate every tool argument in application code.
- [ ] Return structured tool results and stable error types.

### Phase 4 - Safe Agent Orchestration

- [ ] Let the model select from an explicit allowlist of tools.
- [ ] Separate tool proposal from tool execution.
- [ ] Require confirmation for state-changing or sensitive actions.
- [ ] Apply least-privilege authorization outside the model.
- [ ] Limit iterations, time, and tool calls per request.
- [ ] Record the request, decision, approval, tool arguments, result, and failure state in an audit log.

### Phase 5 - Evaluation and Interface

- [ ] Build scenario tests for correct retrieval, tool choice, argument construction, approval handling, and refusal behavior.
- [ ] Add a UI that clearly distinguishes advice, proposed actions, completed actions, and failures.
- [ ] Show citations and tool activity to the technician.
- [ ] Add observability, Docker, CI/CD, and deployment only after the core workflow is reliable.

## Recommended First Slice

Build one complete vertical scenario before introducing embeddings or a complex agent framework:

> A technician reports that a fictional user cannot access VPN. The assistant retrieves the VPN KB article and similar resolved tickets, explains the likely checks, and may invoke a read-only mock tool to inspect the fictional user's VPN/account state.

This slice should use SQLite plus simple deterministic text/tag search. It will establish data contracts, provenance, citations, tool boundaries, and tests without prematurely coupling the project to a vector database or orchestration framework.

## Current Data-Foundation Files

```text
knowledge.py
knowledge_repository.py
data/
  seed.json
  knowledge.db  # generated locally; ignored by Git
mockdata/
  IT Services - Configure VPN Client on your Computer, Tablet, or Phone.pdf
```

Keep storage and simple search together in `knowledge_repository.py` initially. Foundation tests are in `tests/test_knowledge.py` and `tests/test_knowledge_repository.py`, with a shared fictional fixture in `tests/conftest.py`. Do not create tool or orchestration modules yet.

## Guardrails

- Use only synthetic, public, sanitized, or explicitly authorized information.
- Never commit credentials, personal data, customer data, or confidential employer documentation.
- Treat retrieved text and ticket content as untrusted input that may contain prompt injection.
- Give the model access only to registered tools and validated arguments.
- Require explicit user confirmation before any state-changing action.
- Prefer mock or sandbox tools until authorization, audit, and failure handling are tested.
- Make tool outcomes visible; do not claim success unless the tool returned a confirmed success result.

## Next Session

1. Resume from the completed foundation: all 47 tests pass, including the user's tunnel-group example. The user has received an explanation of the testing process and instructions for manual searches; no user-run manual test results have been reported.
2. Propose grounded API integration: retrieve public VPN context for `POST /questions`, supply selected context to the model, return citations, and define missing-evidence behavior. Explain the files and obtain approval before implementation.
3. Keep repository/retrieval regressions passing and use mocked model calls for API integration tests. Ticket data and tools remain deferred.

Today's completed scope: deterministic document search, helper refactor, and passing foundation tests. The VPN-only data foundation is complete. Grounded API answers are the next phase, pending review and approval.

## End-of-Day Handoff

- The user chose to stop here for today. No API integration has been started or approved.
- The user understands that search returns in-memory `SearchResult` objects for later model use; these results are not saved to SQLite.
- Discussed keyword search as the baseline, with vector or hybrid retrieval deferred until realistic evaluations demonstrate a benefit.
- Manual workflow shared: run `.venv\Scripts\python.exe knowledge_repository.py`, start `.venv\Scripts\python.exe`, import `search_documents`, and inspect returned records or `results[0].excerpt`. Try relevant questions, unrelated keywords, service filters, empty permissions, and blank input.
- Automated verification command: `.venv\Scripts\python.exe -m pytest -q`. Last result: 47 passed, one Starlette/httpx deprecation warning. No paid model calls.
