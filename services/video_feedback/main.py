from uuid import UUID
from uuid import uuid4

from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.output_parsers import OutputFixingParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.runnables.history import RunnableWithMessageHistory
from sqlalchemy.orm import Session

from config import current_provider
from models import FeedbackCreate, FeedbackQuestion, Feedback, Analysis
from repositories.chat_history import get_session_history, get_chat_history
from repositories.feedback import create_feedback_analysis, get_feedback_model
from .parser import analysis_output_parser
from .prompt import analysis_system_prompt_with_format, contextualize_q_prompt, qa_prompt
from ..pinecone_utils import create_index, store_document_to_index, get_retriever_from_index, get_index_name
from ..gemini_ai import isTranscriptMatch


def create_feedback(dto: FeedbackCreate, db: Session):
    # Identifier
    feedback_id = uuid4()
    namespace = str(feedback_id)

    # Docs
    loader = PyPDFLoader(dto.context_url.unicode_string())
    pages = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    transcript_texts_docs = text_splitter.create_documents([dto.transcript], [
        {
            "source": "transcript",
            "description": "transcript generated from video presentation rehearsal"
        }
    ])

    # Pinecone
    index_name = get_index_name()
    create_index(current_provider.embedding_dimension, index_name)
    store_document_to_index(pages + transcript_texts_docs, current_provider.embedding, index_name, namespace)
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

    isMatch = isTranscriptMatch(pages, dto.transcript)
    analysis_result, feedback = create_feedback_analysis(db, feedback_id, index_name, response_answer, isMatch)

    feedback.analysis = analysis_result
    feedback.chat_history = []

    return feedback


def get_feedback(feedback_id: UUID, db: Session):
    feedback = get_feedback_model(db, feedback_id)
    chat_history = get_chat_history(db, feedback_id)
    feedback.chat_history = chat_history

    return feedback


def ask_feedback(feedback: Feedback, dto: FeedbackQuestion):
    retriever = get_retriever_from_index(current_provider.embedding, feedback.index_name, str(feedback.id))

    history_aware_retriever = create_history_aware_retriever(
        current_provider.model, retriever, contextualize_q_prompt
    )

    question_answer_chain = create_stuff_documents_chain(current_provider.model, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    response = conversational_rag_chain.invoke({
        "input": dto.question,
        "analysis": convert_analyisis_to_text(feedback.analysis)
    },
        config={
            "configurable": {"session_id": str(feedback.id)},
        },
    )

    response_answer = response['answer']

    return response_answer


def convert_analyisis_to_text(analysis: Analysis):
    analysis_text = f"""
    Analysis Result:
    1. Goods: {", ".join(analysis.goods)}
    2. Bads: {", ".join(analysis.bads)}
    3. Corrections: {", ".join(analysis.corrections)}
    4. Suggestions: {", ".join(analysis.suggestions)}
    5. Overall Feedback: {analysis.overall_feedback}
    """

    return analysis_text
