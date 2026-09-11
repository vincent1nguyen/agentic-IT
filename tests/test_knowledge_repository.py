import json
import sqlite3
from contextlib import closing
from datetime import datetime

import pytest

from knowledge_repository import DEFAULT_SEED_PATH, load_seed, search_documents


@pytest.fixture
def store(tmp_path):
    seed = tmp_path / "seed.json"
    database = tmp_path / "nested" / "knowledge.db"

    def write(documents, tickets=None):
        seed.write_text(json.dumps({"documents": documents, "tickets": tickets or []}), encoding="utf-8")
        return load_seed(seed, database)

    return write, database


def test_loading_updates_without_duplicates_and_retains_other_records(store, document_record):
    write, database = store
    assert write([document_record, document_record | {"id": "retained"}]) == 2
    assert write([document_record]) == 1
    updated = document_record | {"title": "Updated VPN guide", "tags": ["newtag"],
                                 "updated_at": "2026-09-10T00:00:00+00:00"}
    assert write([updated]) == 1
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 2
        row = connection.execute("SELECT title, tags, updated_at FROM documents WHERE id = ?",
                                 (document_record["id"],)).fetchone()
    assert row[:2] == (updated["title"], json.dumps(updated["tags"]))
    assert datetime.fromisoformat(row[2]) == datetime.fromisoformat(updated["updated_at"])


@pytest.mark.parametrize("failure", ["invalid", "duplicate", "tickets"])
def test_bad_seed_does_not_change_existing_records(store, document_record, failure):
    write, database = store
    write([document_record])
    changed = document_record | {"title": "Should never be saved"}
    documents = [changed, document_record | {"id": "bad", "content": " "}] if failure == "invalid" else [changed]
    if failure == "duplicate":
        documents.append(changed)
    with pytest.raises(ValueError):
        write(documents, [{"id": "unsupported"}] if failure == "tickets" else [])
    assert search_documents("vpn", database_path=database)[0].title == document_record["title"]


@pytest.mark.parametrize("payload", [[], {}, {"documents": {}}, {"documents": [{"id": "incomplete"}]}])
def test_invalid_seed_does_not_create_database(tmp_path, payload):
    seed, database = tmp_path / "seed.json", tmp_path / "knowledge.db"
    seed.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        load_seed(seed, database)
    assert not database.exists()


def test_database_failure_rolls_back_entire_batch(store, document_record):
    write, database = store
    write([document_record])
    with closing(sqlite3.connect(database)) as connection:
        connection.execute("""CREATE TRIGGER reject_blocked BEFORE INSERT ON documents
            WHEN NEW.id = 'blocked' BEGIN SELECT RAISE(ABORT, 'test failure'); END""")
        connection.commit()
    with pytest.raises(sqlite3.IntegrityError):
        write([document_record | {"title": "Changed"}, document_record | {"id": "blocked"}])
    results = search_documents("vpn", database_path=database)
    assert [(r.id, r.title) for r in results] == [(document_record["id"], document_record["title"])]


def test_filters_enforce_permissions_and_service_before_limit(store, document_record):
    write, database = store
    write([document_record,
           document_record | {"id": "internal", "sensitivity": "internal"},
           document_record | {"id": "restricted", "sensitivity": "restricted"},
           document_record | {"id": "other-service", "service": "wifi"}])
    assert [r.id for r in search_documents("vpn", service=" VPN ", limit=1, database_path=database)] == ["vpn-guide"]
    results = search_documents("vpn", permitted_sensitivities=("internal",), database_path=database)
    assert [r.id for r in results] == ["internal"]
    assert results[0].sensitivity == "internal"
    assert search_documents("vpn", permitted_sensitivities=(), database_path=database) == []
    assert search_documents("vpn", service="vpn' OR 1=1 --", database_path=database) == []


def test_ranking_weights_distinct_words_and_stable_ties(store, document_record):
    write, database = store
    base = document_record | {"title": "Reference", "tags": [], "content": "Instructions"}
    write([base | {"id": "content", "content": "vpn " * 100},
           base | {"id": "tags", "tags": ["vpn"]},
           base | {"id": "title-b", "title": "VPN"},
           base | {"id": "title-a", "title": "VPN"}])
    results = search_documents("VPN vpn", database_path=database)
    assert [r.id for r in results] == ["title-a", "title-b", "tags", "content"]
    assert search_documents("vpn", limit=2, database_path=database) == results[:2]


def test_whole_words_hyphens_and_source_metadata(store, document_record):
    write, database = store
    write([document_record | {"tags": ["secure-connect"]}])
    result, = search_documents("SECURE connect", database_path=database)
    assert result.source_reference == document_record["source_reference"]
    assert result.is_synthetic is True
    assert result.record_type == "document"
    assert result.excerpt == document_record["content"]
    assert search_documents("vp", database_path=database) == []


@pytest.mark.parametrize("query", ["unrelatedprinter", "which should we use", "?!"])
def test_empty_search_results(store, document_record, query):
    write, database = store
    write([document_record])
    assert search_documents(query, database_path=database) == []


def test_empty_store(store):
    write, database = store
    assert write([]) == 0
    assert search_documents("vpn", database_path=database) == []


@pytest.mark.parametrize("kwargs", [
    {"query": " "}, {"limit": 0}, {"limit": -1}, {"limit": True}, {"limit": 1.5},
    {"service": " "}, {"permitted_sensitivities": ("secret",)},
    {"permitted_sensitivities": "public"},
])
def test_invalid_search_inputs_fail_before_database_access(tmp_path, kwargs):
    with pytest.raises(ValueError):
        search_documents(**({"query": "vpn", "database_path": tmp_path / "missing.db"} | kwargs))


def test_missing_database_is_not_created(tmp_path):
    database = tmp_path / "missing.db"
    with pytest.raises(sqlite3.OperationalError):
        search_documents("vpn", database_path=database)
    assert not database.exists()


def test_real_vpn_excerpt_contains_group_selection_rules(tmp_path):
    database = tmp_path / "knowledge.db"
    load_seed(DEFAULT_SEED_PATH, database)
    result, = search_documents("Which Secure Connect tunnel group should we use?",
                               service="vpn", database_path=database)
    excerpt = " ".join(result.excerpt.split())
    assert "Route only campus traffic" in excerpt
    assert "Route all traffic" in excerpt
    assert "secure-connect options" in excerpt
    assert "required to comply" in excerpt
    assert "Secure Connect NAC" in excerpt
    assert "allthruucsd" in excerpt
    assert result.source_reference.endswith("sysparm_article=KB0020109")
    assert result.is_synthetic is False
    assert result.sensitivity == "public"
    source = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))["documents"][0]["content"]
    assert result.excerpt.removeprefix("… ").removesuffix(" …") in source
