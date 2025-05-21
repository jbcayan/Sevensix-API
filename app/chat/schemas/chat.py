from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    message: str = Field(..., description="The message from the user")


class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    reply: str = Field(..., description="The reply from the system")


class SourceDocument(BaseModel):
    """Model for source documents in chat responses."""
    source: str = Field(..., description="The source of the document")
    content: str = Field(..., description="A snippet of the document content")


class ChatResponseWithSources(ChatResponse):
    """Response model for chat endpoints with sources."""
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used for the reply")