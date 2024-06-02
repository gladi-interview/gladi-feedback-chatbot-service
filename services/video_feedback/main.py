from uuid import uuid4

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain.output_parsers import OutputFixingParser

from config import current_provider
from models import FeedbackCreate, model
from .prompt import analysis_system_prompt_with_format
from .parser import analysis_output_parser

from ..pinecone_utils import create_index, store_document_to_index, get_retriever_from_index, get_index_name
from sqlalchemy.orm import Session


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

    # Database
    feedback = model.Feedback(
        id=feedback_id,
        content_is_matched_with_context=True,
    )

    analysis_result = model.Analysis(
        feedback_id=feedback.id,
        goods=response_answer.goods,
        bads=response_answer.bads,
        corrections=response_answer.corrections,
        suggestions=response_answer.suggestions,
        overall_feedback=response_answer.feedback,
    )

    db.add(feedback)
    db.add(analysis_result)
    db.commit()

    db.refresh(analysis_result)
    db.refresh(feedback)

    feedback.analysis = analysis_result

    return feedback


def get_feedback():
    pass


def ask_feedback():
    pass
