import time
import os

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from dependencies.settings import get_settings

settings = get_settings()
os.environ.setdefault('PINECONE_API_KEY', settings.PINECONE_API_KEY)


def create_index(embedding_dimension: int, index_name: str):
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)

    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

    return True


def get_index_name(base_index_name="feedback-index"):
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    indexes = pc.list_indexes().names()
    total_index = len(indexes)

    if total_index == 0:
        return f'{base_index_name}-0'

    latest_index_name = indexes[total_index - 1]
    latest_index = pc.Index(latest_index_name)
    total_namespace = len(latest_index.describe_index_stats()['namespaces'])
    max_free_namespace = 100

    return latest_index_name if total_namespace < max_free_namespace else f'{base_index_name}-{total_index}'


def delete_index(index_name: str):
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    pc.delete_index(index_name)


def store_document_to_index(docs, embedding, index_name, namespace):
    PineconeVectorStore.from_documents(docs, embedding, index_name=index_name, namespace=namespace)


def store_text_to_index(texts, embedding, index_name, namespace):
    PineconeVectorStore.from_texts(texts, embedding, index_name=index_name, namespace=namespace)


def get_retriever_from_index(embedding, index_name, namespace):
    vector_store = PineconeVectorStore(index_name=index_name, embedding=embedding, namespace=namespace)
    return vector_store.as_retriever(search_kwargs={"k": 10})
