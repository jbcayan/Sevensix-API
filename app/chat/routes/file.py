import os
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models.user import User
from app.accounts.permissions import get_current_user, admin_required
from app.chat.models.file import File as FileModel, InfoType
from app.chat.schemas.file import FileOut
from app.config.database import get_db
from app.config.settings import settings
from app.config import settings as app_settings

BASE_DIR = app_settings.BASE_DIR

# Create the upload directory if it doesn't exist
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

admin_files_router = APIRouter(
    dependencies=[Depends(admin_required)],
)


@admin_files_router.get("", response_model=List[FileOut])
async def get_user_files(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get all files uploaded by the current user."""
    stmt = select(FileModel).where(FileModel.user_uid == current_user.uid).order_by(FileModel.uploaded_at.desc())
    result = await db.execute(stmt)
    files = result.scalars().all()
    return files


@admin_files_router.post("", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
        file: UploadFile = File(...),
        information_type: str = Form("Public"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Upload a new file."""
    # Validate information type
    try:
        info_type = InfoType(information_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid information type. Must be one of: {', '.join([t.value for t in InfoType])}"
        )

    # Create file record in database
    file_record = FileModel(
        filename=file.filename,
        user_uid=current_user.uid,
        information_type=info_type,
    )

    # Save file to disk
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        # Add file record to database
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        return file_record

    except Exception as e:
        # Cleanup if something went wrong
        if os.path.exists(file_path):
            os.remove(file_path)
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while uploading the file: {str(e)}"
        )


@admin_files_router.delete("/{file_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
        file_uid: str = Path(..., description="The UID of the file to delete"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete a file."""
    # Get the file from the database
    stmt = select(FileModel).where(FileModel.uid == file_uid)
    result = await db.execute(stmt)
    file: FileModel | None = result.scalars().first()

    # Check if file exists
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Check if user has permission to delete the file
    if file.user_uid != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Delete the file using the model's async_delete method
    await file.async_delete(db)

    # Return no content
    return None
