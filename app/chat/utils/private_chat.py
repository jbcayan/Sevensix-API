import os
import logging
from app.config import settings as app_settings

from app.config.settings import settings

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

logger = logging.getLogger(__name__)

# Path to persist Chromadb for private chat (relative to project root or setting)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
PRIVATE_DB_PATH = os.path.join(BASE_DIR, "private_chroma_db")

COLLECTION_NAME = "PRIVATE_CHAT_COLLECTION"

# Embeddings and vector store using API key from settings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=settings.OPENAI_API_KEY
)

private_vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PRIVATE_DB_PATH,
)

# Retriever
private_retriever = private_vector_store.as_retriever(search_kwargs={"k": 3})

# LLM model
chat_model = app_settings.private_chat_model

# QA Chain
private_qa_chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    chain_type="stuff",
    retriever=private_retriever,
    return_source_documents=True,
)

def ask(question: str) -> dict:
    """
    Run RetrievalQA chain on a user question using the private vector DB.
    Returns:
        dict: {
            'result': answer string,
            'source_documents': list of Document
        }
    """
    try:
        return private_qa_chain.invoke({"query": question})
    except Exception as e:
        logger.exception(f"Error in private chat retrieval for question: {question}")
        return {
            "result": "Sorry, something went wrong while processing your question.",
            "source_documents": []
        }
