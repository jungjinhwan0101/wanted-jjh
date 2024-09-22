FROM python:3.11.10-slim

ENV APP_HOME=/home/service

WORKDIR ${APP_HOME}

# Install System packages
RUN apt-get update

# Install Python packages
RUN pip install --upgrade pip
RUN pip install poetry==1.8.3
COPY poetry.lock ${APP_HOME}/
COPY pyproject.toml ${APP_HOME}/
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-root

# Copy App
COPY ./src ${APP_HOME}/src

# src 아래의 패키지를 패키지 모드로 설치히기 위해서, 다시 의존성 설치 명령을 싱핸한다.
# 이때, 위에서 이미 설치된 패키지는 캐시되어 있으므로 다시 설치되지 않는다.
RUN poetry install --only main


EXPOSE 8000

ENTRYPOINT ["python", "src/wanted_jjh/cli.py"]
