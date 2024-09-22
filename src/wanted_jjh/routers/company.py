from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Header
from sqlalchemy.orm import Session

from wanted_jjh.dtos.company import CreateCompanyDTO
from wanted_jjh.dtos.company import TagDTO
from wanted_jjh.enums import LanguageCode
from wanted_jjh.exceptions import BusinessException
from wanted_jjh.exceptions import CompanyNotFound
from wanted_jjh.exceptions import TagNotFound
from wanted_jjh.routers.utils.db import get_db
from wanted_jjh.schemas.company import CompanyCreateSchema
from wanted_jjh.schemas.company import CompanySchema
from wanted_jjh.schemas.company import CompanySearchSchema
from wanted_jjh.schemas.company import CompanyTagUpdateSchema
from wanted_jjh.services import company as company_services

router = APIRouter()


@router.get(
    "/search", response_model=list[CompanySearchSchema], name="company:search-by-name"
)
def search_company_by_name(
    query: str,
    x_wanted_language: LanguageCode = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
) -> list[CompanySearchSchema]:
    company_dtos = company_services.search_companies_by_name(
        db_session=db_session, name=query, language_code=x_wanted_language
    )

    response_data = [
        CompanySearchSchema(company_name=company_dto.name)
        for company_dto in company_dtos
    ]

    return response_data


@router.get(
    "/tags", response_model=list[CompanySearchSchema], name="company:search-by-tag"
)
def search_company_by_tag(
    query: str,
    x_wanted_language: LanguageCode = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    try:
        company_dtos = company_services.search_company_by_tag(
            db_session=db_session, tag_name=query, language_code=x_wanted_language
        )
    except TagNotFound:
        raise HTTPException(status_code=404, detail="Tag not found")

    response_data = [
        CompanySearchSchema(company_name=company_dto.name)
        for company_dto in company_dtos
    ]

    return response_data


@router.get(
    "/companies/{company_name}",
    response_model=CompanySchema,
    name="company:get-company",
)
def get_company(
    company_name: str,
    x_wanted_language: LanguageCode = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
) -> CompanySchema:
    try:
        company_dto = company_services.get_company_by_name(
            db_session=db_session,
            company_name=company_name,
            language_code=x_wanted_language,
        )
    except CompanyNotFound:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanySchema(company_name=company_dto.name, tags=company_dto.tag_names)


@router.post(
    "/companies",
    response_model=CompanySchema,
    name="company:add-company",
)
def add_company(
    company_create_request_dto: CompanyCreateSchema,
    x_wanted_language: LanguageCode = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    company_dto = company_services.add_company(
        db_session=db_session,
        create_dto=CreateCompanyDTO(
            ko_name=company_create_request_dto.company_name.ko,
            en_name=company_create_request_dto.company_name.en,
            tw_name=company_create_request_dto.company_name.tw,
            tags=[
                TagDTO(
                    ko_name=tag_requsst_dto.tag_name.ko,
                    en_name=tag_requsst_dto.tag_name.en,
                    ja_name=tag_requsst_dto.tag_name.ja,
                    tw_name=tag_requsst_dto.tag_name.tw,
                )
                for tag_requsst_dto in company_create_request_dto.tags
            ],
        ),
        language_code=x_wanted_language,
    )

    return CompanySchema(company_name=company_dto.name, tags=company_dto.tag_names)


@router.put(
    "/companies/{company_name}/tags",
    response_model=CompanySchema,
    name="company:update-company-tags",
)
def update_company_tags(
    company_name: str,
    tags: list[CompanyTagUpdateSchema],
    x_wanted_language: LanguageCode = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    try:
        company_dto = company_services.append_company_tags(
            db_session=db_session,
            company_name=company_name,
            tags=[
                TagDTO(
                    ko_name=tag.tag_name.ko,
                    en_name=tag.tag_name.en,
                    ja_name=tag.tag_name.ja,
                    tw_name=tag.tag_name.tw,
                )
                for tag in tags
            ],
            language_code=x_wanted_language,
        )
    except CompanyNotFound:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanySchema(company_name=company_dto.name, tags=company_dto.tag_names)


@router.delete(
    "/companies/{company_name}/tags/{tag_name}",
    response_model=CompanySchema,
    name="company:delete-company-tag",
)
def delete_company_tag(
    company_name: str,
    tag_name: str,
    x_wanted_language: LanguageCode = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
) -> CompanySchema:
    try:
        company_dto = company_services.delete_company_tag(
            db_session=db_session,
            company_name=company_name,
            delete_tag_name=tag_name,
            language_code=x_wanted_language,
        )
    except CompanyNotFound:
        raise HTTPException(status_code=404, detail="Company not found")
    except TagNotFound:
        raise HTTPException(status_code=404, detail="Tag not found")
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CompanySchema(company_name=company_dto.name, tags=company_dto.tag_names)
