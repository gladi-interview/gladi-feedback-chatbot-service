FROM python:3.12.0-slim

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

# Install pipenv
RUN pip install pipenv

# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY . /app/

# Expose the port
EXPOSE 8081

CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]