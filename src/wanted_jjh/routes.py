from fastapi import APIRouter

from wanted_jjh.routers import company

router = APIRouter()
router.include_router(company.router, tags=["company"])
