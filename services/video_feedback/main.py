from uuid import uuid4

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.output_parsers import OutputFixingParser
from langchain_community.document_loaders import PyPDFLoader
from sqlalchemy.orm import Session
from uuid import UUID

from config import current_provider
from models import FeedbackCreate
from repositories.feedback import create_feedback_analysis, get_feedback_model
from .parser import analysis_output_parser
from .prompt import analysis_system_prompt_with_format
from ..pinecone_utils import create_index, store_document_to_index, get_retriever_from_index, get_index_name


def create_feedback(dto: FeedbackCreate, db: Session):
    # Identifier
    feedback_id = uuid4()
    namespace = str(feedback_id)

    # Docs
    loader = PyPDFLoader(dto.context_url.unicode_string())
    pages = loader.load_and_split()

    # Pinecone
    index_name = get_index_name()
    create_index(current_provider.embedding_dimension, index_name)
    store_document_to_index(pages, current_provider.embedding, index_name, namespace)
    retriever = get_retriever_from_index(current_provider.embedding, index_name, namespace)

    # Chains
    qa_chain = create_stuff_documents_chain(
        llm=current_provider.model,
        prompt=analysis_system_prompt_with_format,
        output_parser=OutputFixingParser.from_llm(
            parser=analysis_output_parser,
            llm=current_provider.model,
            max_retries=2,
        )
    )

    rag_chain = create_retrieval_chain(retriever, qa_chain)

    response = rag_chain.invoke({"input": dto.transcript})
    response_answer = response['answer']

    analysis_result, feedback = create_feedback_analysis(db, feedback_id, index_name, response_answer)

    feedback.analysis = analysis_result

    return feedback


def get_feedback(feedback_id: UUID, db: Session):
    return get_feedback_model(db, feedback_id)


def ask_feedback():
    pass
