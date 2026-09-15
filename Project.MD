# Agentic IT Support Assistant - Project Plan

## Agreed Retrieval Direction — September 15, 2026

Build a LangChain RAG (retrieval-augmented generation) pipeline with FastAPI and
semantic search to retrieve relevant knowledge-base articles and surface cited
sources alongside generated responses. This is the intended implementation and
portfolio goal, not a capability already completed.

The next milestone is article ingestion and semantic retrieval: split the existing
VPN article into coherent passages, retain article/source and passage metadata,
generate embeddings, and retrieve relevant passages through LangChain. Connect
that retriever to the existing grounded FastAPI answer flow. PostgreSQL with
pgvector is a candidate aligned with the broader stack; the vector store,
embedding model, dependencies, and detailed file changes still need a concrete
proposal. Preserve authorization filtering and the separation of retrieved data
from system instructions.

The September 15 retrieval-only evaluation found the correct article for all four
user questions, but its single 160-word excerpt missed important evidence for
tunnel-group selection, Trellix requirements, and username format. An unsupported
package-scripts question returned unrelated Linux installation instructions.
Use these results as the keyword baseline for evaluating semantic retrieval;
semantic similarity does not establish that a passage answers the question.

LangChain and semantic search are now explicit requirements. SQLite FTS5 was
discussed but was not selected as the next step. This direction supersedes earlier
instructions to defer LangChain and embeddings. No RAG migration has been
implemented; see `current.md` for exact evaluation inputs and the current handoff.

### What RAG Means in This Project

RAG is the evidence pipeline used before the model answers:

```text
IT question or fictional ticket
    -> split and index authorized support documents as meaningful chunks
    -> retrieve the chunks most relevant to the issue
    -> pass the question, chunks, and source metadata to the LLM
    -> return a grounded answer, a clarification request, or an evidence-gap response
```

The current keyword baseline successfully identifies the VPN article but often
chooses the wrong passage inside it. Semantic retrieval is intended to improve
passage selection by meaning rather than exact word overlap. It is not a complete
solution by itself: chunk boundaries, metadata filters, top-k results, neighboring
context, reranking, and evidence/answerability checks must be evaluated against known
questions.

### RAG Versus Agentic Behavior

The project has two layers:

1. **RAG assistant:** retrieves evidence and produces a cited answer, clarification,
   or explicit statement that the documentation is insufficient.
2. **Agentic ticket assistant:** can also choose controlled tools, observe their
   results, and continue a bounded workflow—for example, load a fictional ticket,
   check mock VPN/account state, draft a comment, or propose a status change.

A generated answer alone is chatbot/RAG behavior. Tool selection and multi-step
decision-making make the later workflow agentic. The model may propose actions, but
application code owns authorization, approval, execution, limits, and auditing.

## Latest Implementation Update — September 14, 2026

The first grounded API slice is implemented: `/questions` retrieves public VPN
excerpts, sends them to the model with grounding instructions, and returns their
source references. No matches skip the model and return an explicit missing-evidence
answer. Search failures return a safe 503 error. All 52 tests pass without paid model
calls. Live-model answer quality and citation faithfulness remain unevaluated;
returned sources identify supplied context, not independently verified claims.
This supersedes the older API status and immediate-next-milestone sections below.
The user has reviewed this slice. See `current.md` for the next-session handoff.

## Confirmed Product Direction - September 14, 2026

Build an AI-powered mock ServiceNow ticket assistant for IT support staff: investigate
fictional tickets, retrieve supporting documentation, suggest articles, draft service-desk
responses, and perform approved ticket actions in a local mock system.
No real ServiceNow connection is required for this personal-project demonstration.

The API and a future MCP server will expose shared application services. An MCP-compatible
client, such as Claude Code, can use those capabilities without bypassing validation,
permissions, approval, or audit handling. The client may provide its own agent reasoning;
the existing API continues to support the application's model-generated answer flow.

Planned MCP tools:

| Tool | Purpose | Effect |
| --- | --- | --- |
| `search_kb` | Retrieve permitted knowledge excerpts | Read-only |
| `get_ticket` | Retrieve a fictional ticket by ID | Read-only |
| `suggest_kb_articles` | Find relevant articles for a ticket | Read-only |
| `draft_ticket_response` | Generate a grounded reply for review | Returns a draft; does not post it |
| `add_ticket_comment` | Save an approved comment to a mock ticket | State-changing; approval and audit required |
| `update_ticket_status` | Change a mock ticket's status | State-changing; approval and audit required |

### Near-Term Build Order

1. Create section-aware VPN chunks with stable IDs and article, heading, source,
   service, sensitivity, and synthetic-data metadata.
2. Propose and implement the LangChain embedding/vector retrieval layer in small
   approved steps while preserving the original article and authorization filters.
3. Evaluate retrieval independently using the four September 15 questions and
   rewordings. Measure whether required evidence appears in the top results and
   whether unsupported questions are recognized as weak or unanswered.
4. Add hybrid retrieval, neighboring context, reranking, or answerability checks only
   when evaluation shows they are needed. Then connect retrieval to generation and
   evaluate answer grounding, clarification behavior, and citations separately.
   Paid embedding/model calls require explicit opt-in; mock tests remain the default.
5. Add a consistent service-desk reply template: greeting, thank-you, grounded guidance
   or clarification, and configured technician/contact signature. Keep source citations
   available for technician review; do not let the model invent contact details.
6. Add ticket subject/description input and mock ticket persistence with retrieval by ID.
7. Implement investigation and drafting tools using shared application services.
8. Expose those services through MCP.
9. Add approved mock comments/status changes with validation and audit records.

A small technician UI can demonstrate ticket entry, reply review, sources, and copying
the draft once the core workflow is ready. Additional data and each implementation step
remain subject to the working agreement in `current.md`. The broader roadmap below is
long-term guidance; this build order takes precedence for the next sessions.

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
- Adding cloud infrastructure before the core workflow is ready. LangChain and
  semantic search are the agreed next retrieval milestone; PostgreSQL/pgvector
  remains a storage candidate pending the implementation proposal.
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

SQLite is the implemented baseline store. The next semantic retrieval design will
select vector storage; PostgreSQL with pgvector is a candidate that fits the planned
database stack. Preserve the existing source records during that transition.

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

Document chunks and embeddings will be derived data in the next semantic retrieval milestone.

### Starter Dataset

Create 10-20 high-quality records across a few coherent scenarios rather than many shallow documents:

- VPN access and MFA enrollment,
- protected Wi-Fi and certificate errors,
- password reset and account lockout,
- software installation and device compliance.

Include successful tickets, irrelevant tickets, ambiguous cases, outdated documents, and missing-answer cases so retrieval behavior can be evaluated realistically.

## Retrieval Strategy

The implemented baseline uses deterministic title/tag/content keyword scoring,
public/service filters, and one selected excerpt per document. Retain its September
15 evaluation results for comparison.

Next, build the agreed LangChain semantic retrieval pipeline:

1. Split authorized articles into coherent passages while preserving headings,
   source references, stable identifiers, sensitivity, and synthetic-data labels.
2. Generate embeddings and index passages in the selected vector store.
3. Retrieve relevant passages by meaning, allowing multiple passages from one article.
4. Enforce metadata and authorization filters before passages reach the model.
5. Supply retrieved context to grounded generation and expose traceable citations.
6. Evaluate retrieval separately from answer quality against the user's cases and
   rewordings. Consider hybrid search or reranking only if measured gaps justify it.

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

- **Implemented:** Python, FastAPI, Pydantic, OpenAI API, SQLite, Pytest.
- **Next:** LangChain, embeddings, and semantic/vector retrieval; select the embedding
  model and vector store in the implementation proposal. PostgreSQL/pgvector is a candidate.
- **Later:** React, TypeScript, and PostgreSQL if not selected for the retrieval milestone.
- **After reliability is proven:** Docker, GitHub Actions, AWS, and optional sandbox integrations.

LangChain is an explicit requirement for the RAG pipeline. Keep application policy,
approval handling, and API contracts separate from framework-specific integrations.

## Current Repository State

- `main.py` contains the FastAPI app and `/health` and `/questions` endpoints.
- `llm.py` isolates OpenAI configuration and response generation.
- `tests/` contains endpoint and provider tests using test doubles.
- `pyproject.toml` declares Python dependencies.
- The current question response is compatible with future source retrieval but does not yet retrieve data or call tools.
- As of September 10, 2026, the VPN-only data foundation is complete: typed models, one user-supplied public VPN article, repeatable SQLite loading, and deterministic search with filtering, ranked excerpts, and source references.
- All 47 tests pass, including repository/retrieval tests and existing API/provider tests, without paid model calls. See `current.md` for the session handoff and working agreement.

## Immediate Next Milestone

Design and implement LangChain article ingestion and semantic retrieval, following
the September 15 direction and the working agreement in `current.md`:

1. Propose chunking, metadata, embedding model, vector store, dependencies, and files.
2. Obtain approval for the concrete implementation step before changing code.
3. Build and test the ingestion/retrieval layer, then integrate it with `/questions`.
4. Compare retrieval against the four user-provided questions and rewordings.
5. Evaluate live answers and citation support only with explicit opt-in for paid calls.

The immediate dataset remains one public VPN article. Additional seed documents, ticket storage/history, and mock tools are deferred until the user expands scope. The broader roadmap above describes future work.

## Development Principles

- Build the smallest end-to-end scenario first.
- Keep HTTP, orchestration, retrieval, model-provider, policy, and tool-adapter responsibilities separate.
- Use typed boundaries and structured outputs.
- Mock external services in automated tests.
- Do not refactor unrelated code.
- Do not add infrastructure until it solves a demonstrated problem.
- Document completed behavior accurately; do not present planned features as implemented.
- Keep secrets and real organizational data out of Git.
