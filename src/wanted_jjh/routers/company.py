from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Header
from sqlalchemy import and_
from sqlalchemy.orm import Session

from wanted_jjh.enums import LanguageCode
from wanted_jjh.models.company import Company
from wanted_jjh.models.company import CompanyName
from wanted_jjh.models.company_tag import CompanyTag
from wanted_jjh.models.company_tag import CompanyTagName
from wanted_jjh.routers.utils.db import get_db
from wanted_jjh.schemas.company import CompanyCreateSchema
from wanted_jjh.schemas.company import CompanySearchSchema
from wanted_jjh.schemas.company import CompanyTagUpdateSchema

router = APIRouter()


@router.get(
    "/search", response_model=list[CompanySearchSchema], name="company:search-by-name"
)
def search_company_by_name(
    query: str,
    x_wanted_language: str = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    query_result = (
        db_session.query(Company)
        .join(CompanyName)
        .filter(CompanyName.name.like(f"%{query}%"))
        .all()
    )

    return [
        CompanySearchSchema(
            company_name=company.get_name(language_code=x_wanted_language)
        )
        for company in query_result
    ]


@router.get(
    "/tags", response_model=list[CompanySearchSchema], name="company:search-by-tag"
)
def search_company_by_tag(
    query: str,
    x_wanted_language: str = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    tag = (
        db_session.query(CompanyTag)
        .join(CompanyTag.names)
        .filter(CompanyTagName.name == query)
        .first()
    )

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    companies = tag.companies
    unique_companies = {company.id: company for company in companies}.values()

    sorted_companies = sorted(unique_companies, key=lambda x: x.id)

    result: list[CompanySearchSchema] = []
    for company in sorted_companies:
        company_name = company.get_name(x_wanted_language)

        if not company_name:
            for language_code in [
                LanguageCode.ko,
                LanguageCode.en,
                LanguageCode.ja,
                LanguageCode.tw,
            ]:
                company_name = company.get_name(language_code)
                if company_name:
                    break

        result.append(CompanySearchSchema(company_name=company_name))

    return result


@router.get("/companies/{company_name}")
def get_company(
    company_name: str,
    x_wanted_language: str = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    company = (
        db_session.query(Company)
        .join(CompanyName)
        .filter(CompanyName.name == company_name)
        .first()
    )

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    tags = [tag.get_name(x_wanted_language) for tag in company.tags]

    return {"company_name": company.get_name(x_wanted_language), "tags": tags}


@router.post("/companies")
def add_company(
    company_create_dto: CompanyCreateSchema,
    x_wanted_language: str = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    new_company = Company()
    new_company.names.extend(
        [
            CompanyName(
                language_code=LanguageCode.ko, name=company_create_dto.company_name.ko
            ),
            CompanyName(
                language_code=LanguageCode.en, name=company_create_dto.company_name.en
            ),
            CompanyName(
                language_code=LanguageCode.tw, name=company_create_dto.company_name.tw
            ),
        ]
    )

    db_session.add(new_company)
    db_session.commit()
    db_session.refresh(new_company)

    # 태그 처리 (기존 태그 확인 후 연결)
    for tag_dto in company_create_dto.tags:
        tag = (
            db_session.query(CompanyTag)
            .join(CompanyTagName)
            .filter(
                and_(
                    CompanyTagName.language_code == LanguageCode.ko,
                    CompanyTagName.name == tag_dto.tag_name.ko,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.en,
                    CompanyTagName.name == tag_dto.tag_name.en,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.tw,
                    CompanyTagName.name == tag_dto.tag_name.tw,
                )
            )
            .first()
        )

        # 태그가 없으면 새로 추가
        if not tag:
            tag = CompanyTag()
            tag.names.extend(
                [
                    CompanyTagName(
                        language_code=LanguageCode.ko, name=tag_dto.tag_name.ko
                    ),
                    CompanyTagName(
                        language_code=LanguageCode.en, name=tag_dto.tag_name.en
                    ),
                    CompanyTagName(
                        language_code=LanguageCode.tw, name=tag_dto.tag_name.tw
                    ),
                ]
            )
            db_session.add(tag)

        new_company.tags.append(tag)

    db_session.commit()

    company_name = new_company.get_name(x_wanted_language)
    tags = [tag.get_name(x_wanted_language) for tag in new_company.tags]

    return {
        "company_name": company_name,
        "tags": tags,
    }


@router.put("/companies/{company_name}/tags")
async def update_company_tags(
    company_name: str,
    tags: list[CompanyTagUpdateSchema],
    x_wanted_language: str = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    company = (
        db_session.query(Company)
        .join(Company.names)
        .filter(CompanyName.name == company_name)
        .first()
    )

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for tag_dto in tags:
        # 태그 존재 여부 확인
        tag = (
            db_session.query(CompanyTag)
            .join(CompanyTag.names)
            .filter(
                and_(
                    CompanyTagName.language_code == LanguageCode.ko,
                    CompanyTagName.name == tag_dto.tag_name.ko,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.en,
                    CompanyTagName.name == tag_dto.tag_name.en,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.ja,
                    CompanyTagName.name == tag_dto.tag_name.jp,
                )
            )
            .first()
        )

        # 태그가 없으면 새로 추가
        if not tag:
            tag = CompanyTag()
            tag.names.extend(
                [
                    CompanyTagName(
                        language_code=LanguageCode.ko, name=tag_dto.tag_name.ko
                    ),
                    CompanyTagName(
                        language_code=LanguageCode.ja, name=tag_dto.tag_name.jp
                    ),
                    CompanyTagName(
                        language_code=LanguageCode.en, name=tag_dto.tag_name.en
                    ),
                ]
            )
            db_session.add(tag)

        company.tags.append(tag)

    db_session.commit()

    translated_company_name = company.get_name(x_wanted_language)

    translated_tags = [tag.get_name(x_wanted_language) for tag in company.tags]
    sorted_tags = sorted(translated_tags)

    return {
        "company_name": translated_company_name,
        "tags": sorted_tags,
    }


@router.delete("/companies/{company_name}/tags/{tag_name}")
async def delete_company_tag(
    company_name: str,
    tag_name: str,
    x_wanted_language: str = Header(LanguageCode.en),
    db_session: Session = Depends(get_db),
):
    company = (
        db_session.query(Company)
        .join(CompanyName)
        .filter(CompanyName.name == company_name)
        .first()
    )

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    tag_to_remove = (
        db_session.query(CompanyTag)
        .join(CompanyTag.names)
        .filter(CompanyTagName.name == tag_name)
        .first()
    )

    if not tag_to_remove:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag_to_remove in company.tags:
        company.tags.remove(tag_to_remove)
    else:
        raise HTTPException(
            status_code=404, detail="Tag not associated with this company"
        )

    db_session.commit()

    tags = sorted([t.get_name(x_wanted_language) for t in company.tags])

    return {
        "company_name": company.get_name(x_wanted_language),
        "tags": tags,
    }
