import pytest
from pydantic import ValidationError

from knowledge import Document, SearchResult, Ticket


@pytest.mark.parametrize("field", ["id", "title", "content", "service", "source_reference"])
def test_document_rejects_blank_text(document_record, field):
    document_record[field] = " \n "
    with pytest.raises(ValidationError):
        Document.model_validate(document_record)


@pytest.mark.parametrize("changes", [
    {"tags": [" "]}, {"sensitivity": "secret"},
    {"document_type": "unknown"}, {"created_at": "yesterday"},
])
def test_document_rejects_invalid_metadata(document_record, changes):
    with pytest.raises(ValidationError):
        Document.model_validate(document_record | changes)


def test_document_normalizes_text_and_preserves_provenance(document_record):
    document_record["title"] = "  VPN guide  "
    document = Document.model_validate(document_record)
    assert document.title == "VPN guide"
    assert document.source_reference == "fixture://vpn-guide"
    assert document.sensitivity == "public"
    assert document.is_synthetic is True
    assert document.created_at.tzinfo is not None


@pytest.mark.parametrize("score", [-1, float("inf"), float("nan")])
def test_result_rejects_invalid_score(document_record, score):
    with pytest.raises(ValidationError):
        SearchResult.model_validate(document_record | {
            "record_type": "document", "excerpt": "VPN instructions", "score": score,
        })


def test_ticket_accepts_unresolved_case_and_rejects_blank_resolution():
    record = dict(
        id="fictional-ticket", summary="VPN unavailable", symptoms="Connection fails",
        category="network", service="vpn", status="open", source_reference="fixture://ticket",
        sensitivity="internal", is_synthetic=True, opened_at="2026-09-09T00:00:00Z",
    )
    assert Ticket.model_validate(record).resolution is None
    with pytest.raises(ValidationError):
        Ticket.model_validate(record | {"resolution": " "})
