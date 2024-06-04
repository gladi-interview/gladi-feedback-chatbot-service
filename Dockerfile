FROM python:3.12.0-alpine

ARG LANGCHAIN_TRACING_V2
ARG LANGCHAIN_API_KEY
ARG OPENAI_API_KEY
ARG SQLALCHEMY_DATABASE_URL
ARG GCP_PROJECT_ID
ARG PINECONE_API_KEY
ARG GEMINI_AI_KEY

ENV LANGCHAIN_TRACING_V2=$LANGCHAIN_TRACING_V2
ENV LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV SQLALCHEMY_DATABASE_URL=$SQLALCHEMY_DATABASE_URL
ENV GCP_PROJECT_ID=$GCP_PROJECT_ID
ENV PINECONE_API_KEY=$PINECONE_API_KEY
ENV GEMINI_AI_KEY=$GEMINI_AI_KEY

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pip install pipenv

RUN  \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache libgeos-dev && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pipenv install --system --deploy --ignore-pipfile && \
    apk --purge del .build-deps

COPY . /app/

EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]