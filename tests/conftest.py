import pytest


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
