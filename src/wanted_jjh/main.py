from fastapi import FastAPI

from wanted_jjh.routes import router
from wanted_jjh import settings
from wanted_jjh.db.session import DBBase
from wanted_jjh.db.session import Session
from wanted_jjh.db.session import engine
from starlette.requests import Request

DBBase.metadata.create_all(engine)


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME, debug=settings.DEBUG, version=settings.VERSION
    )
    application.include_router(router)

    return application


app = get_application()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = Session()
    response = await call_next(request)
    request.state.db.close()
    return response
