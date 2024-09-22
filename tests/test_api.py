from starlette.testclient import TestClient

from wanted_jjh.db.session import Session
from wanted_jjh.enums import LanguageCode
from wanted_jjh.models.company import Company
from wanted_jjh.models.company import CompanyName
from wanted_jjh.models.company_tag import CompanyTag
from wanted_jjh.models.company_tag import CompanyTagName


def test_company_name_autocomplete(api: TestClient, db_session: Session):
    """
    1. 회사명 자동완성
    회사명의 일부만 들어가도 검색이 되어야 합니다.
    header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """
    # Arrange
    company1 = Company()
    company2 = Company()
    company3 = Company()
    db_session.add_all([company1, company2, company3])
    db_session.commit()

    db_session.add_all(
        [
            CompanyName(
                company_id=company1.id, language_code="ko", name="주식회사 링크드코리아"
            ),
            CompanyName(company_id=company2.id, language_code="ko", name="스피링크"),
        ]
    )
    db_session.commit()

    # Act
    resp = api.get("/search?query=링크", headers=[("x-wanted-language", "ko")])

    # Assert
    searched_companies = resp.json()

    assert resp.status_code == 200
    assert searched_companies == [
        {"company_name": "주식회사 링크드코리아"},
        {"company_name": "스피링크"},
    ]


def test_company_search(api: TestClient, db_session: Session):
    """
    2. 회사 이름으로 회사 검색
    header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """
    # Arrange
    company = Company()
    db_session.add(company)
    db_session.commit()

    db_session.add_all(
        [
            CompanyName(company_id=company.id, language_code="en", name="Wantedlab"),
            CompanyName(company_id=company.id, language_code="ko", name="원티드랩"),
        ]
    )
    db_session.commit()

    company_tag = CompanyTag()
    company_tag.names.append(
        CompanyTagName(tag_id=company_tag.id, language_code="ko", name="태그_4"),
    )
    db_session.add(company_tag)
    company.tags.append(company_tag)

    company_tag = CompanyTag()
    company_tag.names.append(
        CompanyTagName(tag_id=company_tag.id, language_code="ko", name="태그_20"),
    )
    db_session.add(company_tag)
    company.tags.append(company_tag)

    company_tag = CompanyTag()
    company_tag.names.append(
        CompanyTagName(tag_id=company_tag.id, language_code="ko", name="태그_16"),
    )
    db_session.add(company_tag)
    company.tags.append(company_tag)

    db_session.commit()

    # Act
    resp = api.get("/companies/Wantedlab", headers=[("x-wanted-language", "ko")])

    # Assert
    company = resp.json()
    assert resp.status_code == 200
    assert company == {
        "company_name": "원티드랩",
        "tags": [
            "태그_4",
            "태그_20",
            "태그_16",
        ],
    }

    # 검색된 회사가 없는경우 404를 리턴합니다.
    resp = api.get("/companies/없는회사", headers=[("x-wanted-language", "ko")])

    assert resp.status_code == 404


def test_new_company(api: TestClient):
    """
    3.  새로운 회사 추가
    새로운 언어(tw)도 같이 추가 될 수 있습니다.
    저장 완료후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """
    resp = api.post(
        "/companies",
        json={
            "company_name": {
                "ko": "라인 프레쉬",
                "tw": "LINE FRESH",
                "en": "LINE FRESH",
            },
            "tags": [
                {
                    "tag_name": {
                        "ko": "태그_1",
                        "tw": "tag_1",
                        "en": "tag_1",
                    }
                },
                {
                    "tag_name": {
                        "ko": "태그_8",
                        "tw": "tag_8",
                        "en": "tag_8",
                    }
                },
                {
                    "tag_name": {
                        "ko": "태그_15",
                        "tw": "tag_15",
                        "en": "tag_15",
                    }
                },
            ],
        },
        headers=[("x-wanted-language", "tw")],
    )

    company = resp.json()
    assert company == {
        "company_name": "LINE FRESH",
        "tags": [
            "tag_1",
            "tag_8",
            "tag_15",
        ],
    }


def test_search_tag_name(api: TestClient, db_session: Session):
    """
    4.  태그명으로 회사 검색
    태그로 검색 관련된 회사가 검색되어야 합니다.
    다국어로 검색이 가능해야 합니다.
    일본어 태그로 검색을 해도 language가 ko이면 한국 회사명이 노출이 되어야 합니다.
    ko언어가 없을경우 노출가능한 언어로 출력합니다.
    동일한 회사는 한번만 노출이 되어야합니다.
    """
    # Arrange
    target_tag_name = "タグ_22"
    tag = CompanyTag()
    tag.names.append(CompanyTagName(language_code="ja", name=target_tag_name))
    db_session.add(tag)
    db_session.commit()

    def make_company(*, ko_name: str = "", en_name: str = ""):
        company = Company()
        (
            company.names.extend(
                [
                    CompanyName(language_code="ko", name=ko_name),
                    CompanyName(language_code="en", name=en_name),
                ]
            ),
        )
        company.tags.append(tag)
        db_session.add(company)
        db_session.commit()

    make_company(ko_name="딤딤섬 대구점")
    make_company(ko_name="마이셀럽스")
    make_company(en_name="Rejoice Pregnancy")
    make_company(ko_name="삼일제약")
    make_company(ko_name="투게더앱스")

    # Act
    resp = api.get(
        f"/tags?query={target_tag_name}", headers=[("x-wanted-language", "ko")]
    )
    searched_companies = resp.json()

    assert [company["company_name"] for company in searched_companies] == [
        "딤딤섬 대구점",
        "마이셀럽스",
        "Rejoice Pregnancy",
        "삼일제약",
        "투게더앱스",
    ]


def test_new_tag(api: TestClient, db_session: Session):
    """
    5.  회사 태그 정보 추가
    저장 완료후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """
    # Arrange
    company = Company()
    company.names.extend(
        [
            CompanyName(language_code=LanguageCode.ko, name="원티드랩"),
            CompanyName(language_code=LanguageCode.en, name="Wantedlab"),
        ]
    )

    tag = CompanyTag()
    tag.names.extend(
        [
            CompanyTagName(language_code=LanguageCode.ko, name="태그_16"),
            CompanyTagName(language_code=LanguageCode.en, name="tag_16"),
        ]
    )
    company.tags.append(tag)

    tag = CompanyTag()
    tag.names.extend(
        [
            CompanyTagName(language_code=LanguageCode.ko, name="태그_20"),
            CompanyTagName(language_code=LanguageCode.en, name="tag_20"),
        ]
    )
    company.tags.append(tag)

    db_session.add(company)
    db_session.commit()

    # Act
    resp = api.put(
        "/companies/원티드랩/tags",
        json=[
            {
                "tag_name": {
                    "ko": "태그_50",
                    "ja": "タグ_50",
                    "en": "tag_50",
                }
            },
            {
                "tag_name": {
                    "ko": "태그_4",
                    "tw": "tag_4",
                    "en": "tag_4",
                }
            },
        ],
        headers=[("x-wanted-language", "en")],
    )

    # Assert
    company = resp.json()
    assert company == {
        "company_name": "Wantedlab",
        "tags": [
            "tag_16",
            "tag_20",
            "tag_4",
            "tag_50",
        ],
    }


def test_delete_tag(api: TestClient, db_session: Session):
    """
    6.  회사 태그 정보 삭제
    저장 완료후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """
    # Arrange
    company = Company()
    company.names.extend(
        [
            CompanyName(language_code=LanguageCode.ko, name="원티드랩"),
            CompanyName(language_code=LanguageCode.en, name="Wantedlab"),
        ]
    )

    tag = CompanyTag()
    tag.names.extend(
        [
            CompanyTagName(language_code=LanguageCode.ko, name="태그_16"),
            CompanyTagName(language_code=LanguageCode.en, name="tag_16"),
        ]
    )
    company.tags.append(tag)

    tag = CompanyTag()
    tag.names.extend(
        [
            CompanyTagName(language_code=LanguageCode.ko, name="태그_20"),
            CompanyTagName(language_code=LanguageCode.en, name="tag_20"),
        ]
    )
    company.tags.append(tag)

    tag = CompanyTag()
    tag.names.extend(
        [
            CompanyTagName(language_code=LanguageCode.ko, name="태그_4"),
            CompanyTagName(language_code=LanguageCode.en, name="tag_4"),
        ]
    )
    company.tags.append(tag)

    tag = CompanyTag()
    tag.names.extend(
        [
            CompanyTagName(language_code=LanguageCode.ko, name="태그_50"),
            CompanyTagName(language_code=LanguageCode.en, name="tag_50"),
        ]
    )
    company.tags.append(tag)

    db_session.add(company)
    db_session.commit()

    # Act
    resp = api.delete(
        "/companies/원티드랩/tags/태그_16",
        headers=[("x-wanted-language", "en")],
    )

    # Assert
    company = resp.json()
    assert company == {
        "company_name": "Wantedlab",
        "tags": [
            "tag_20",
            "tag_4",
            "tag_50",
        ],
    }
