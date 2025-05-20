import os
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.chat.models.file import File, InfoType
from app.chat.utils.private_chat import private_vector_store
from app.chat.utils.public_chat import public_vector_store
from app.config import settings as app_settings

logger = logging.getLogger(__name__)

# Ensure the uploads folder exists
UPLOAD_DIR = os.path.join(app_settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Text splitter config
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
)

async def process_file(file_record: File) -> str:
    """
    Process one uploaded file:
    - Choose the correct Chroma store based on `information_type`
    - Remove existing embeddings
    - Load and tag the document
    - Split it into chunks
    - Upsert into Chroma
    
    Returns:
        str: The new status of the file ("Processed", "Error", or "Unsupported Format")
    """
    try:
        store = private_vector_store if file_record.information_type == InfoType.PRIVATE else public_vector_store
        file_path = file_record.get_upload_path()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")

        # Step 1: Delete any existing vectors
        store.delete(where={"source": file_record.filename})

        # Step 2: Load the document
        ext = os.path.splitext(file_record.filename)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            return "Unsupported Format"

        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = file_record.filename

        # Step 3: Chunk + Upsert
        chunks = splitter.split_documents(docs)
        store.add_documents(chunks)

        return "Processed"
    
    except Exception as e:
        logger.exception(f"Error processing file {file_record.filename}")
        return "Error"