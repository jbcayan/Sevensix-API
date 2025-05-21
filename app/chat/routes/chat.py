import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models.user import User
from app.accounts.permissions import get_current_user
from app.chat.models.conversation import Conversation, ConversationType
from app.chat.schemas.chat import ChatRequest, ChatResponse, ChatResponseWithSources, SourceDocument
from app.chat.utils.public_chat import public_ask
from app.config.database import get_db

logger = logging.getLogger(__name__)

# Create routers
public_chat_router = APIRouter()
private_chat_router = APIRouter()


@public_chat_router.post("", response_model=ChatResponseWithSources)
async def public_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Public chat endpoint that doesn't require authentication.
    Processes the user's message and returns a reply.
    """
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )

    # Call the public_ask function to get a reply
    output = public_ask(message)
    reply = output.get('result')
    source_docs = output.get('source_documents', [])

    # Format the sources
    sources = [
        {
            'source': doc.metadata.get('source'),
            'content': doc.page_content[:200]
        }
        for doc in source_docs
    ]

    # For public chats, we can now save the conversation with a NULL user_uid
    conversation = Conversation(
        user_uid=None,  # Now we can use None for public conversations
        conversation_type=ConversationType.PUBLIC,
        query=message,
        answer=reply,
        sources=sources
    )
    db.add(conversation)
    await db.commit()

    # Return the reply with sources
    return ChatResponseWithSources(reply=reply, sources=sources)
