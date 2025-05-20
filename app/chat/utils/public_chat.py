import os
import logging
from app.config import settings as app_settings
from app.config.settings import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

logger = logging.getLogger(__name__)

# Set project base directory relative to this file's location
BASE_DIR = app_settings.BASE_DIR
PUBLIC_DB_PATH = os.path.join(BASE_DIR, "public_chroma_db")

COLLECTION_NAME = "PUBLIC_CHAT_COLLECTION"

# Init embeddings with OpenAI API key from settings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=settings.OPENAI_API_KEY
)
public_vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PUBLIC_DB_PATH
)

public_retriever = public_vector_store.as_retriever(search_kwargs={"k": 3})
chat_model = app_settings.public_chat_model

public_qa_chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    chain_type="stuff",
    retriever=public_retriever,
    return_source_documents=True
)

def public_ask(question: str) -> dict:
    try:
        return public_qa_chain.invoke({"query": question})
    except Exception as e:
        logger.exception(f"Error in public chat retrieval for question: {question}")
        return {
            "result": "Sorry, something went wrong while answering your question.",
            "source_documents": []
        }