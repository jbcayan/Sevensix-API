import asyncio
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models.file import File as FileModel
from app.chat.utils.process_file import process_file

logger = logging.getLogger(__name__)


async def process_file_background(file_uid: str, db: AsyncSession):
    """
    Background task to process a file and update its status in the database.
    """
    # Get the file from the database
    stmt = select(FileModel).where(FileModel.uid == file_uid)
    result = await db.execute(stmt)
    file: FileModel | None = result.scalars().first()

    if file is None:
        logger.error(f"File with UID {file_uid} not found for processing")
        return

    # Process the file
    new_status = await process_file(file)

    # Update the file status in the database
    stmt = update(FileModel).where(FileModel.uid == file_uid).values(status=new_status)
    await db.execute(stmt)
    await db.commit()
