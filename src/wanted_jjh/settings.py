import os

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME: str = "wanted_jjh"
VERSION: str = "0.1.0"
DEBUG: bool = False

SQLALCHEMY_DATABASE_URL: str = os.getenv(
    "DATABASE_URI", f"sqlite:///{BASE_DIR}/wanted_jjh.sqlite"
)
