from sqlalchemy import and_

from wanted_jjh.db.session import Session
from wanted_jjh.dtos.company import CompanyDTO
from wanted_jjh.dtos.company import CreateCompanyDTO
from wanted_jjh.dtos.company import TagDTO
from wanted_jjh.enums import LanguageCode
from wanted_jjh.exceptions import BusinessException
from wanted_jjh.exceptions import CompanyNotFound
from wanted_jjh.exceptions import TagNotFound
from wanted_jjh.models.company import Company
from wanted_jjh.models.company import CompanyName
from wanted_jjh.models.company_tag import CompanyTag
from wanted_jjh.models.company_tag import CompanyTagName


def search_companies_by_name(
    *, db_session: Session, name: str, language_code: LanguageCode = LanguageCode.ko
) -> list[CompanyDTO]:
    companies = (
        db_session.query(Company)
        .join(CompanyName)
        .filter(CompanyName.name.like(f"%{name}%"))
        .all()
    )

    company_dtos = [
        CompanyDTO(name=company.get_name(language_code=language_code))
        for company in companies
    ]

    return company_dtos


def search_company_by_tag(
    *, db_session: Session, tag_name: str, language_code: LanguageCode = LanguageCode.ko
) -> list[CompanyDTO]:
    tag = (
        db_session.query(CompanyTag)
        .join(CompanyTag.names)
        .filter(CompanyTagName.name == tag_name)
        .first()
    )

    if not tag:
        raise TagNotFound(f"{tag_name} 태그가 존재하지 않습니다.")

    companies = tag.companies
    unique_companies = {company.id: company for company in companies}.values()

    sorted_companies = sorted(unique_companies, key=lambda x: x.id)

    company_dtos = []
    for company in sorted_companies:
        company_name = company.get_name(language_code)

        if not company_name:
            for lan_code in [
                LanguageCode.ko,
                LanguageCode.en,
                LanguageCode.ja,
                LanguageCode.tw,
            ]:
                company_name = company.get_name(lan_code)
                if company_name:
                    break

        company_dtos.append(CompanyDTO(name=company_name))

    return company_dtos


def to_company_dto(company: Company, language_code: LanguageCode) -> CompanyDTO:
    translated_company_name = company.get_name(language_code)
    translated_tags = [tag.get_name(language_code) for tag in company.tags]
    sorted_tags = sorted(translated_tags)

    return CompanyDTO(
        name=translated_company_name,
        tag_names=sorted_tags,
    )


def get_company_by_name(
    *,
    db_session: Session,
    company_name: str,
    language_code: LanguageCode = LanguageCode.ko,
) -> CompanyDTO:
    company = (
        db_session.query(Company)
        .join(CompanyName)
        .join(Company.tags)
        .filter(CompanyName.name == company_name)
        .first()
    )

    if not company:
        raise CompanyNotFound(f"{company_name} 회사가 존재하지 않습니다.")

    return CompanyDTO(
        name=company.get_name(language_code),
        tag_names=[tag.get_name(language_code) for tag in company.tags],
    )


def add_company(
    *,
    db_session: Session,
    create_dto: CreateCompanyDTO,
    language_code: LanguageCode = LanguageCode.ko,
) -> CompanyDTO:
    new_company = Company()
    new_company.names.extend(
        [
            CompanyName(language_code=LanguageCode.ko, name=create_dto.ko_name),
            CompanyName(language_code=LanguageCode.en, name=create_dto.en_name),
            CompanyName(language_code=LanguageCode.tw, name=create_dto.tw_name),
        ]
    )

    db_session.add(new_company)
    db_session.commit()
    db_session.refresh(new_company)

    # 태그 처리 (기존 태그 확인 후 연결)
    for tag_dto in create_dto.tags:
        tag = (
            db_session.query(CompanyTag)
            .join(CompanyTagName)
            .filter(
                and_(
                    CompanyTagName.language_code == LanguageCode.ko,
                    CompanyTagName.name == tag_dto.ko_name,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.en,
                    CompanyTagName.name == tag_dto.en_name,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.tw,
                    CompanyTagName.name == tag_dto.tw_name,
                )
            )
            .first()
        )

        # 태그가 없으면 새로 추가
        if not tag:
            tag = CompanyTag()
            tag.names.extend(
                [
                    CompanyTagName(language_code=LanguageCode.ko, name=tag_dto.ko_name),
                    CompanyTagName(language_code=LanguageCode.en, name=tag_dto.en_name),
                    CompanyTagName(language_code=LanguageCode.tw, name=tag_dto.tw_name),
                ]
            )
            db_session.add(tag)

        new_company.tags.append(tag)

    db_session.commit()

    return to_company_dto(new_company, language_code)


def append_company_tags(
    *,
    db_session: Session,
    company_name: str,
    tags: list[TagDTO],
    language_code: LanguageCode = LanguageCode.ko,
):
    company = (
        db_session.query(Company)
        .join(Company.names)
        .join(Company.tags)
        .filter(CompanyName.name == company_name)
        .first()
    )

    if not company:
        raise CompanyNotFound(f"{company_name} 회사가 존재하지 않습니다.")

    for tag_dto in tags:
        # 태그 존재 여부 확인
        tag = (
            db_session.query(CompanyTag)
            .join(CompanyTag.names)
            .filter(
                and_(
                    CompanyTagName.language_code == LanguageCode.ko,
                    CompanyTagName.name == tag_dto.ko_name,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.en,
                    CompanyTagName.name == tag_dto.en_name,
                )
                | and_(
                    CompanyTagName.language_code == LanguageCode.ja,
                    CompanyTagName.name == tag_dto.ja_name,
                )
            )
            .first()
        )

        # 태그가 없으면 새로 추가
        if not tag:
            tag = CompanyTag()
            tag.names.extend(
                [
                    CompanyTagName(language_code=LanguageCode.ko, name=tag_dto.ko_name),
                    CompanyTagName(language_code=LanguageCode.ja, name=tag_dto.ja_name),
                    CompanyTagName(language_code=LanguageCode.en, name=tag_dto.en_name),
                ]
            )
            db_session.add(tag)

        company.tags.append(tag)

    db_session.commit()

    return to_company_dto(company, language_code)


def delete_company_tag(
    *,
    db_session: Session,
    company_name: str,
    delete_tag_name: str,
    language_code: LanguageCode = LanguageCode.ko,
) -> CompanyDTO:
    company = (
        db_session.query(Company)
        .join(CompanyName)
        .join(Company.tags)
        .filter(CompanyName.name == company_name)
        .first()
    )

    if not company:
        raise CompanyNotFound(f"{company_name} 회사가 존재하지 않습니다.")

    tag_to_remove = (
        db_session.query(CompanyTag)
        .join(CompanyTag.names)
        .filter(CompanyTagName.name == delete_tag_name)
        .first()
    )

    if not tag_to_remove:
        raise TagNotFound(f"{delete_tag_name} 태그가 존재하지 않습니다.")

    if tag_to_remove in company.tags:
        company.tags.remove(tag_to_remove)
    else:
        raise BusinessException("Tag not associated with this company")

    db_session.commit()

    return to_company_dto(company, language_code)
