"""Validated records for the synthetic knowledge store and its search results."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints


# Match the API's convention: trim whitespace and reject blank text.
NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sensitivity = Literal["public", "internal", "restricted"]


class Document(BaseModel):
    """A knowledge article, procedure, policy, or reference document."""

    id: NonBlankText
    title: NonBlankText
    document_type: Literal["kb_article", "procedure", "policy", "reference"]
    content: NonBlankText
    service: NonBlankText
    tags: list[NonBlankText] = Field(default_factory=list)
    source_reference: NonBlankText
    sensitivity: Sensitivity
    is_synthetic: bool
    created_at: datetime
    updated_at: datetime


class Ticket(BaseModel):
    """A support case whose symptoms and resolution can inform retrieval."""

    id: NonBlankText
    summary: NonBlankText
    symptoms: NonBlankText
    resolution: NonBlankText | None = None
    category: NonBlankText
    service: NonBlankText
    status: Literal["open", "resolved", "closed"]
    tags: list[NonBlankText] = Field(default_factory=list)
    related_document_ids: list[NonBlankText] = Field(default_factory=list)
    source_reference: NonBlankText
    sensitivity: Sensitivity
    is_synthetic: bool
    opened_at: datetime
    resolved_at: datetime | None = None


class SearchResult(BaseModel):
    """A ranked match with enough source information for a citation."""

    id: NonBlankText
    record_type: Literal["document", "ticket"]
    title: NonBlankText
    excerpt: NonBlankText
    score: float = Field(ge=0, allow_inf_nan=False)
    source_reference: NonBlankText
    sensitivity: Sensitivity
    is_synthetic: bool
