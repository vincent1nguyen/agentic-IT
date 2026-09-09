# Agentic IT Support Assistant - Project Plan

## Project Vision

Build a full-stack IT support assistant that can understand a technician's request, retrieve relevant internal context, choose from a controlled set of tools, and perform authorized actions safely.

The project begins with synthetic internal data that resembles real support resources:

- knowledge-base articles,
- internal process documentation,
- relevant historical tickets,
- fictional users, devices, accounts, and services used by mock tools.

The result should demonstrate practical agentic AI engineering, not unrestricted automation. The application owns permissions, validation, approval, execution, and auditing; the model may recommend or select an action only within those boundaries.

## Primary Goals

1. Provide grounded IT guidance with traceable citations.
2. Allow the assistant to select appropriate tools from an explicit registry.
3. Execute read-only and simulated state-changing IT actions through typed adapters.
4. Require approval for consequential actions and enforce least privilege outside the model.
5. Build a realistic but entirely synthetic internal knowledge and ticket dataset.
6. Evaluate the assistant's retrieval, decisions, tool use, and final responses with deterministic tests.
7. Grow into a portfolio-quality React, TypeScript, FastAPI, PostgreSQL, Docker, CI/CD, and AWS application incrementally.

## Non-Goals for the First Version

- Connecting to a real employer's systems or copying confidential documentation.
- Giving the model unrestricted shell, network, database, or administrative access.
- Automatically performing destructive or high-impact actions.
- Adding embeddings, LangChain, PostgreSQL, or cloud infrastructure before a simpler implementation proves the contracts and workflow.
- Claiming autonomous remediation when actions are mocked or require technician approval.

## Target User Experience

A technician describes an issue. The assistant retrieves related internal documentation and ticket resolutions, then does one of the following:

- answers with cited troubleshooting steps,
- asks for missing information,
- proposes an available tool and explains why it is useful,
- runs a safe read-only tool,
- requests confirmation before a state-changing tool,
- reports the verified result or a clear failure.

Example:

```text
Technician: Taylor cannot connect to the VPN after changing phones.

Assistant:
- Found the VPN enrollment guide and two similar resolved tickets.
- The account may still be bound to the previous MFA device.
- Proposed read-only action: inspect Taylor's fictional MFA/VPN status.

[Run check]

Tool result:
- VPN account: enabled
- MFA enrollment: old device only

Assistant:
- Recommended next step: start the mock MFA re-enrollment workflow.
- This changes account state and requires technician confirmation.

[Approve] [Cancel]
```

## Core Architecture

```text
React / TypeScript UI
          |
          v
FastAPI API and authentication context
          |
          v
Assistant orchestration service
    |           |             |
    v           v             v
Retrieval   Policy/approval   Tool registry
    |                         |
    v                         v
Synthetic knowledge DB    Controlled adapters
          \                 /
           v               v
             OpenAI model
          (reasoning/selection)
                  |
                  v
       Structured response + audit event
```

The model does not directly access the database or external systems. Application services expose narrow retrieval and tool interfaces, validate all inputs, and decide whether execution is permitted.

## Synthetic Internal Data

### Data Policy

All repository data must be public, synthetic, sanitized, or explicitly authorized. Do not copy workplace KB articles, ticket text, names, email addresses, hostnames, credentials, tokens, or customer information into the project.

Synthetic records should be labeled as synthetic and use fictional identifiers. Each record should include provenance and sensitivity metadata so filtering can be tested from the start.

### Initial Store

Use SQLite for the first local implementation because it is simple, deterministic, and sufficient for learning the data and retrieval contracts. Introduce PostgreSQL and pgvector later when scale or semantic retrieval creates a concrete need.

Suggested tables:

```text
documents
- id
- title
- document_type (kb_article, procedure, policy, reference)
- content
- service
- tags
- sensitivity
- source_reference
- is_synthetic
- created_at
- updated_at

tickets
- id
- external_reference
- summary
- symptoms
- resolution
- category
- service
- status
- tags
- related_document_ids
- is_synthetic
- opened_at
- resolved_at

audit_events
- id
- request_id
- actor
- event_type
- tool_name
- redacted_arguments
- approval_state
- outcome
- created_at
```

Document chunks and embeddings should be derived data, added only when semantic retrieval is introduced.

### Starter Dataset

Create 10-20 high-quality records across a few coherent scenarios rather than many shallow documents:

- VPN access and MFA enrollment,
- protected Wi-Fi and certificate errors,
- password reset and account lockout,
- software installation and device compliance.

Include successful tickets, irrelevant tickets, ambiguous cases, outdated documents, and missing-answer cases so retrieval behavior can be evaluated realistically.

## Retrieval Strategy

Start with deterministic keyword, tag, service, document-type, and recency scoring. Return structured results containing a stable ID, title, excerpt, score, and source reference.

Then evolve in measured steps:

1. SQLite full-text search if basic matching becomes limiting.
2. Chunking and embeddings for semantic similarity.
3. Hybrid retrieval combining lexical and vector scores.
4. Metadata and authorization filtering before results enter the prompt.
5. Reranking only if evaluations show a benefit.

The assistant should state when evidence is weak or absent. It must not invent internal procedures or citations.

## Tool System

### Tool Contract

Every tool should define:

- a unique name and human-readable description,
- a typed argument schema,
- a typed result schema,
- read-only or state-changing classification,
- required permission,
- approval policy,
- timeout and failure behavior,
- fields that must be redacted from logs.

Tool calls pass through a registry and executor. Unknown tools and invalid arguments are rejected before any adapter runs.

### Initial Mock Tools

Begin with read-only tools:

- `lookup_user` - return a fictional user's support profile.
- `lookup_device` - return mock enrollment and compliance state.
- `check_vpn_status` - return mock VPN and MFA status.
- `search_ticket_history` - query synthetic resolved tickets.

Then add simulated state-changing tools:

- `create_ticket_draft`,
- `request_password_reset`,
- `start_mfa_reenrollment`.

State-changing tools should initially update only local mock state and must require explicit approval. Idempotency keys should prevent accidental duplicate actions.

## Agent Orchestration

Use a bounded state machine rather than an open-ended autonomous loop:

```text
RECEIVE
  -> RETRIEVE_CONTEXT
  -> DECIDE
       -> ANSWER
       -> CLARIFY
       -> PROPOSE_TOOL
  -> VALIDATE_POLICY
       -> AWAIT_APPROVAL (when required)
       -> EXECUTE_TOOL
  -> OBSERVE_RESULT
  -> RESPOND
```

Set limits for model turns, tool calls, execution time, and result size. Preserve request and tool-call identifiers across the workflow. A model-generated tool request is a proposal; only the policy/execution layer can authorize it.

## Safety and Trust Boundaries

- Treat user input, retrieved documents, and ticket history as untrusted content.
- Keep system instructions and tool policy separate from retrieved text.
- Filter data by authorization before model exposure.
- Use allowlisted tools with least-privilege credentials.
- Require confirmation for state-changing, sensitive, costly, or externally visible actions.
- Never expose secrets or raw provider errors.
- Redact sensitive arguments and results from logs.
- Record approvals and tool outcomes in an append-only audit trail.
- Report only verified tool outcomes; distinguish proposals, attempts, successes, and failures.
- Provide a kill switch or configuration setting that disables all action tools.

## API Direction

Preserve `POST /questions` during the transition, then introduce a conversation/action contract that can represent multiple states.

Possible response shape:

```json
{
  "request_id": "req_123",
  "status": "answer|clarification_required|approval_required|completed|failed",
  "message": "Human-readable response",
  "sources": [],
  "proposed_action": null,
  "tool_result": null
}
```

Approval should be a separate API operation tied to a stored proposal and request ID. The client must not be able to alter approved tool arguments by resubmitting a modified payload.

## Development Roadmap

### Phase 1 - Data Foundation

- Define Pydantic/domain models and SQLite schema.
- Create synthetic seed fixtures.
- Implement idempotent database initialization.
- Build repository methods and deterministic retrieval.
- Test ranking, filtering, provenance, and empty results.

Exit criteria: a query can return useful, cited documents and ticket resolutions without calling an LLM.

### Phase 2 - Grounded Knowledge Assistant

- Connect retrieval to the existing question endpoint.
- Construct prompts from authorized results.
- Return source citations.
- Handle insufficient evidence explicitly.
- Add grounding and prompt-injection test cases.

Exit criteria: tested questions produce useful responses supported by synthetic sources.

### Phase 3 - Read-Only Tool Calling

- Build the typed tool registry and executor.
- Implement fictional directory, device, and VPN tools.
- Allow the model to choose a tool through structured output/tool calling.
- Validate arguments and record audit events.
- Add tool-selection and failure-path evaluations.

Exit criteria: the assistant reliably selects and executes the correct read-only mock tool for defined scenarios.

### Phase 4 - Approval and Mock Actions

- Add persisted action proposals and approval states.
- Add local simulated write tools.
- Enforce authorization, explicit confirmation, idempotency, and timeouts.
- Display proposed and completed actions distinctly.
- Test cancellation, replay, expired approval, partial failure, and denial.

Exit criteria: no state-changing mock tool can execute without a valid stored approval.

### Phase 5 - Frontend

- Build a React and TypeScript technician interface.
- Show answers, sources, clarification requests, action proposals, approvals, results, and errors.
- Make action boundaries obvious to the user.
- Add component and Playwright workflow tests.

### Phase 6 - Production-Oriented Storage and Retrieval

- Migrate to PostgreSQL when justified.
- Add pgvector or another vector store if semantic retrieval improves evaluations.
- Add hybrid search, background ingestion, document versioning, and retention rules.
- Keep retrieval and tool interfaces stable during infrastructure changes.

### Phase 7 - Reliability and Deployment

- Add structured logging, tracing, metrics, and evaluation reporting.
- Containerize the application.
- Run tests and security checks in GitHub Actions.
- Deploy to an appropriate AWS environment.
- Add secret management, backups, rate limits, and operational runbooks.

### Phase 8 - Optional Real Integrations

Only after mock workflows are safe and reliable, consider sandbox integrations such as ServiceNow, an identity provider, or device management system. Use scoped service accounts, vendor sandboxes, explicit approvals, and read-only access first.

## Testing and Evaluation

Automated tests must not make paid model calls unless explicitly separated as opt-in evaluations.

Test layers:

- repository and schema tests,
- deterministic retrieval tests,
- API contract tests,
- tool validation and authorization tests,
- orchestration state-transition tests,
- prompt-injection and data-boundary tests,
- mocked model/tool integration tests,
- curated scenario evaluations,
- frontend end-to-end tests.

Track scenario-level measures such as retrieval relevance, citation accuracy, correct tool selection, valid arguments, unnecessary tool-call rate, approval compliance, task success, and safe refusal behavior.

## Technology Strategy

- **Now:** Python, FastAPI, Pydantic, OpenAI API, SQLite, Pytest.
- **After the workflow is proven:** React, TypeScript, PostgreSQL, embeddings/vector search.
- **After reliability is proven:** Docker, GitHub Actions, AWS, and optional sandbox integrations.

Frameworks such as LangChain may be introduced if they reduce demonstrated orchestration or retrieval complexity. The core application contracts should not depend on a framework unnecessarily.

## Current Repository State

- `main.py` contains the FastAPI app and `/health` and `/questions` endpoints.
- `llm.py` isolates OpenAI configuration and response generation.
- `tests/` contains endpoint and provider tests using test doubles.
- `pyproject.toml` declares Python dependencies.
- The current question response is compatible with future source retrieval but does not yet retrieve data or call tools.

## Immediate Next Milestone

Implement a synthetic VPN support vertical slice:

1. Define models and an SQLite schema for documents and tickets.
2. Seed a VPN KB article, an MFA procedure, several related resolved tickets, and irrelevant controls.
3. Implement deterministic retrieval with citations.
4. Test relevance, filtering, ordering, and empty results.
5. Add a read-only mock VPN-status tool only after retrieval is independently working.

## Development Principles

- Build the smallest end-to-end scenario first.
- Keep HTTP, orchestration, retrieval, model-provider, policy, and tool-adapter responsibilities separate.
- Use typed boundaries and structured outputs.
- Mock external services in automated tests.
- Do not refactor unrelated code.
- Do not add infrastructure until it solves a demonstrated problem.
- Document completed behavior accurately; do not present planned features as implemented.
- Keep secrets and real organizational data out of Git.

