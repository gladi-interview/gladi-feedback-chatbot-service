from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .parser import analysis_output_parser

analysis_system_prompt = """
You are a presentation evaluator. You have been asked to evaluate a presentation rehearsal based on the given generated video transcript and context. 
Note that the transcript is generated by an AI system which may contain typos, missing words, and misrecognized words.

You are to evaluate the presentation rehearsal from the transcript content based on the given context (if needed) 
with the following criteria:
1. list of good things from presentation
2. list of bad things from presentation
3. list of corrections from presentation
4. list of suggestions for improvement
5. overall feedback in maximum five sentences

context: {context}
output format: {format_instructions}
"""

# Analysis prompt
analysis_prompt = ChatPromptTemplate.from_messages([
    ('system', analysis_system_prompt),
    ('human', 'transcript from rehearsal: {input}')
])

analysis_system_prompt_with_format = analysis_prompt.partial(
    format_instructions=analysis_output_parser.get_format_instructions())


# Contextualize question prompt
contextualize_q_system_prompt = """
Given a chat history and the latest user question which might reference context in the chat history.
Formulate a standalone question which can be understood without the chat history. 
Do NOT answer the question, just reformulate it if needed and otherwise return it as is.
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Question prompt
qa_system_prompt = """
You are an assistant for question-answering tasks related to a presentation. 
You have analyzed the presentation rehearsal and summarize it based on the given transcript content and context. 
You are to answer the following question based on the context and your previous analysis with maximum ten sentences to answer the question. 
If you don't know the answer or the questions is not related to the presentation, just say it.

context: {context}
previous analysis: {analysis}
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "Question: {input}"),
    ]
)
