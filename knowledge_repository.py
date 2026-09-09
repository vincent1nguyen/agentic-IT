"""Load validated seed documents into a local SQLite database."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from knowledge import Document


# Resolve paths relative to this file, regardless of the terminal's directory.
DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
DEFAULT_DATABASE_PATH = DATA_DIRECTORY / "knowledge.db"
DEFAULT_SEED_PATH = DATA_DIRECTORY / "seed.json"


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
