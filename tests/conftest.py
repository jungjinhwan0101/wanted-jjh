import os
from typing import Generator

import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from wanted_jjh.main import get_application

from wanted_jjh.db.session import DBBase
from wanted_jjh.routers.utils.db import get_db

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLALCHEMY_DATABASE_URL: str = os.getenv("TEST_DATABASE_URI", "sqlite://")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, None, None]:
    DBBase.metadata.create_all(engine)
    yield get_application()
    DBBase.metadata.drop_all(engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[Session, None, None]:
    connection = engine.connect()

    transaction = connection.begin()

    session = Session(bind=connection)

    yield session

    session.close()

    transaction.rollback()

    connection.close()


@pytest.fixture
def api(app: FastAPI, db_session: Session) -> Generator[TestClient, None, None]:
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db

    with TestClient(app) as client:
        yield client
