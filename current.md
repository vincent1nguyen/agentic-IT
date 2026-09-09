# Current Development Session

Date: September 8, 2026

## Current Goal

Evolve the project from a question-answering knowledge assistant into an agentic IT support assistant that can retrieve internal context, choose an appropriate tool, and safely perform approved support actions.

The immediate milestone is to design and build a synthetic internal-data foundation containing knowledge-base articles, internal documentation, and relevant ticket history. All data must be fictional, sanitized, or explicitly authorized.

## Current State

- The project has a working FastAPI application in `main.py`.
- `GET /health` returns `{ "status": "ok" }`.
- `POST /questions` validates nonblank input and generates an answer through the OpenAI provider in `llm.py`.
- The response contract is currently `{ "answer": string, "sources": [] }`.
- Provider configuration and failures are mapped to safe HTTP errors.
- Automated tests use test doubles and do not make paid OpenAI API requests.
- Retrieval, a mock internal database, tool calling, action approval, and audit logging have not been implemented yet.

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

### Phase 1 - Synthetic Internal Data

- [ ] Define a common schema for knowledge articles, internal documents, and ticket history.
- [ ] Create a small, clearly synthetic dataset covering two or three IT support scenarios.
- [ ] Store structured records in SQLite for the first implementation.
- [ ] Add deterministic repository/search functions and tests.
- [ ] Add provenance and sensitivity metadata to every record.

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

## Files Expected in the Next Milestone

```text
data/
  seed/
    documents.json
    tickets.json

models/
  knowledge.py
  tools.py

services/
  knowledge_repository.py
  retrieval.py

tools/
  registry.py
  mock_it.py

tests/
  test_knowledge_repository.py
  test_retrieval.py
  test_tools.py
```

The exact structure should follow the repository as it evolves; do not create modules until the current milestone needs them.

## Guardrails

- Use only synthetic, public, sanitized, or explicitly authorized information.
- Never commit credentials, personal data, customer data, or confidential employer documentation.
- Treat retrieved text and ticket content as untrusted input that may contain prompt injection.
- Give the model access only to registered tools and validated arguments.
- Require explicit user confirmation before any state-changing action.
- Prefer mock or sandbox tools until authorization, audit, and failure handling are tested.
- Make tool outcomes visible; do not claim success unless the tool returned a confirmed success result.

## Next Session

Implement Phase 1 as a small vertical slice:

1. Finalize the SQLite schema and typed models.
2. Create synthetic VPN knowledge and ticket fixtures.
3. Add a seed/load path that is safe to run repeatedly.
4. Implement deterministic keyword/tag retrieval.
5. Add tests for filtering, ranking, citations, and empty results.
6. Connect retrieval to `POST /questions` only after the repository layer is independently tested.

