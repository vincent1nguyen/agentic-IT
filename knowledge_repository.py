"""Load and search validated documents in a local SQLite database."""

import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from knowledge import Document, SearchResult, Sensitivity


# Resolve paths relative to this file, regardless of the terminal's directory.
DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
DEFAULT_DATABASE_PATH = DATA_DIRECTORY / "knowledge.db"
DEFAULT_SEED_PATH = DATA_DIRECTORY / "seed.json"

# Ignore conversational words so they do not create irrelevant matches.
STOP_WORDS = frozenset(
    "a an and are as at be by can do does for from how i in is it me my of on "
    "or our should that the their this to use we what when where which who "
    "why with would you your".split()
)


def _keywords(text: str) -> set[str]:
    """Match whole words, treating case and hyphens consistently."""
    return set(re.findall(r"\w+", text.casefold())) - STOP_WORDS


def _relevant_excerpt(content: str, query_words: set[str]) -> str:
    """Select a source passage using word coverage, then matching frequency.

    Overlapping 160-word windows keep nearby instructions together. Excerpts
    preserve the original text; ellipses indicate omitted surrounding content.
    """
    words = list(re.finditer(r"\S+", content))
    best_start = 0
    best_end = len(content)
    best_score = (-1, -1)
    for index in range(0, len(words), 20):
        start = words[index].start()
        end = words[min(index + 159, len(words) - 1)].end()
        passage_words = re.findall(r"\w+", content[start:end].casefold())
        score = (
            len(query_words.intersection(passage_words)),
            sum(word in query_words for word in passage_words),
        )
        # Equal scores retain the earliest passage for deterministic results.
        if score > best_score:
            best_start, best_end, best_score = start, end, score
    excerpt = content[best_start:best_end]
    return ("… " if best_start else "") + excerpt + (
        " …" if best_end < len(content) else ""
    )


def _validate_search_inputs(
    query: str,
    permitted_sensitivities: tuple[Sensitivity, ...],
    service: str | None,
    limit: int,
) -> None:
    """Reject invalid search inputs before accessing the database."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be nonblank text.")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive integer.")
    if isinstance(permitted_sensitivities, str) or any(
        value not in ("public", "internal", "restricted")
        for value in permitted_sensitivities
    ):
        raise ValueError("Invalid permitted sensitivity.")
    if service is not None:
        if not isinstance(service, str) or not service.strip():
            raise ValueError("Service must be nonblank text when supplied.")


def _read_documents(
    database_path: Path,
    permitted_sensitivities: tuple[Sensitivity, ...],
    service: str | None,
) -> list[Document]:
    """Read permitted records using filtered SQL and validate stored documents."""
    if not permitted_sensitivities:
        return []

    placeholders = ", ".join("?" for _ in permitted_sensitivities)
    sql = f"SELECT * FROM documents WHERE sensitivity IN ({placeholders})"
    parameters: list[str] = list(permitted_sensitivities)
    if service is not None:
        sql += " AND service = ? COLLATE NOCASE"
        parameters.append(service.strip())

    # Read-only mode avoids creating an empty database if the path is wrong.
    uri = database_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(sql, parameters).fetchall()

    documents = []
    for row in rows:
        record = dict(row)
        record["tags"] = json.loads(record["tags"])
        documents.append(Document.model_validate(record))
    return documents


def _score_document(document: Document, query_words: set[str]) -> int:
    """Weight distinct keyword matches in the title, tags, and content."""
    return (
        3 * len(query_words & _keywords(document.title))
        + 2 * len(query_words & _keywords(" ".join(document.tags)))
        + len(query_words & _keywords(document.content))
    )


def search_documents(
    query: str,
    *,
    permitted_sensitivities: tuple[Sensitivity, ...] = ("public",),
    service: str | None = None,
    limit: int = 5,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> list[SearchResult]:
    """Return filtered keyword matches, ordered by score then document ID.

    Each distinct query word scores 3 for a title match, 2 for a tag match,
    and 1 for a content match. Scores are lexical weights, not confidence.
    The caller must supply sensitivity permissions from trusted application
    policy, never from model output. Only public documents are allowed by default.

    Blank queries/filters and invalid limits raise ValueError. Queries with no
    searchable words, no permissions, or no matches return an empty list.
    A missing/uninitialized database raises a SQLite error; run load_seed first.
    """
    _validate_search_inputs(query, permitted_sensitivities, service, limit)
    query_words = _keywords(query)
    if not query_words or not permitted_sensitivities:
        return []

    documents = _read_documents(database_path, permitted_sensitivities, service)
    results = []
    for document in documents:
        score = _score_document(document, query_words)
        if score == 0:
            continue
        results.append(
            SearchResult(
                id=document.id,
                record_type="document",
                title=document.title,
                excerpt=_relevant_excerpt(document.content, query_words),
                score=score,
                source_reference=document.source_reference,
                sensitivity=document.sensitivity,
                is_synthetic=document.is_synthetic,
            )
        )
    return sorted(results, key=lambda result: (-result.score, result.id))[:limit]


def load_seed(
    seed_path: Path = DEFAULT_SEED_PATH,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> int:
    """Validate all documents, then insert or update them in one transaction.

    Returns the number of documents processed. Documents absent from the seed
    are kept. Ticket loading will be added when ticket data is introduced.
    """
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    if not isinstance(seed, dict) or not isinstance(seed.get("documents"), list):
        raise ValueError("Seed data must contain a documents list.")
    if seed.get("tickets"):
        raise ValueError("Ticket loading is not supported yet.")

    # Validate the entire batch before creating or changing the database.
    documents = [Document.model_validate(record) for record in seed["documents"]]
    ids = [document.id for document in documents]
    if len(ids) != len(set(ids)):
        raise ValueError("Seed documents must have unique IDs.")

    database_path.parent.mkdir(parents=True, exist_ok=True)
    # The transaction context commits on success and rolls back on failure;
    # closing() also closes the connection afterward.
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY NOT NULL,
                    title TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    service TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    source_reference TEXT NOT NULL,
                    sensitivity TEXT NOT NULL,
                    is_synthetic INTEGER NOT NULL CHECK (is_synthetic IN (0, 1)),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            for document in documents:
                # SQLite stores tags as JSON text and dates as ISO 8601 text.
                values = document.model_dump(mode="json")
                values["tags"] = json.dumps(values["tags"])
                values["is_synthetic"] = int(document.is_synthetic)
                connection.execute(
                    """
                    INSERT INTO documents (
                        id, title, document_type, content, service, tags,
                        source_reference, sensitivity, is_synthetic,
                        created_at, updated_at
                    ) VALUES (
                        :id, :title, :document_type, :content, :service, :tags,
                        :source_reference, :sensitivity, :is_synthetic,
                        :created_at, :updated_at
                    )
                    ON CONFLICT(id) DO UPDATE SET
                        title = excluded.title,
                        document_type = excluded.document_type,
                        content = excluded.content,
                        service = excluded.service,
                        tags = excluded.tags,
                        source_reference = excluded.source_reference,
                        sensitivity = excluded.sensitivity,
                        is_synthetic = excluded.is_synthetic,
                        created_at = excluded.created_at,
                        updated_at = excluded.updated_at
                    """,
                    values,
                )

    return len(documents)


if __name__ == "__main__":
    count = load_seed()
    print(f"Loaded {count} document(s) into {DEFAULT_DATABASE_PATH}")
