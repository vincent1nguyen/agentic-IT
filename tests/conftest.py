import pytest

from knowledge import SearchResult


@pytest.fixture
def search_result():
    return SearchResult(
        id="vpn-guide", record_type="document", title="VPN guide",
        excerpt="Select the VPN profile assigned to your device.", score=3,
        source_reference="fixture://vpn-guide", sensitivity="public",
        is_synthetic=True,
    )


@pytest.fixture
def document_record():
    """Small fictional record; never added to the project's seed dataset."""
    return {
        "id": "vpn-guide",
        "title": "VPN guide",
        "document_type": "kb_article",
        "content": "Select the VPN profile assigned to your device.",
        "service": "vpn",
        "tags": ["vpn"],
        "source_reference": "fixture://vpn-guide",
        "sensitivity": "public",
        "is_synthetic": True,
        "created_at": "2026-09-09T00:00:00+00:00",
        "updated_at": "2026-09-09T00:00:00+00:00",
    }
