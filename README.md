# Wanted JJH

### Tech Stack
- Python 3.11.x
- FastAPI 0.115.x
- SQLAlchemy 2.0.x
- Docker
- SQLite


### 개발환경 구축
```bash
# 파이썬 의존성 설치
pip install poetry
poetry install

# 테스트 실행
pytest tests/

# 개발 DB 초기화
# sqlite db file path : src/wanted_jjh.sqlite
# 실행하고 나면 DB가 생성되고, 테이블이 마이그레이션이 되며, 초기 데이터가 삽입된다.
poetry run python data/setup_init_db.py

# 서버 실행(8000번 포트로 FastAPI 서버가 실행된다)
poetry run python src/wanted_jjh/cli.py

# code format & lint check
poetry run ruff check src/
```

### 로컬 Docker Container 서버 배포방법
```
# 1. 로컬 서버 배포 및 실행
sh ./deploy_local.sh

# 2. Container 가 바라보는 DB 초기화
sh init_db_local_container.sh 
```

### API 명세
서버 실행 후, 다음의 URL로 접속하면 API 명세를 확인할 수 있다.
http://0.0.0.0:8000/docs
