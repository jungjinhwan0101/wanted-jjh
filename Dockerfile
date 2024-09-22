FROM python:3.11.10-slim

ENV APP_HOME=/home/service

WORKDIR ${APP_HOME}

# Copy App
COPY ./src ${APP_HOME}/src

# Install System packages
RUN apt-get update

# Install Python packages
RUN pip install --upgrade pip
RUN pip install poetry==1.8.3
COPY poetry.lock ${APP_HOME}/
COPY pyproject.toml ${APP_HOME}/
RUN poetry config virtualenvs.create false
RUN poetry install --only main

EXPOSE 8000

ENTRYPOINT ["python", "src/wanted_jjh/cli.py"]
