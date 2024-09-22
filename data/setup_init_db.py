import csv

from sqlalchemy import and_

from wanted_jjh.db.session import DBBase
from wanted_jjh.db.session import Session
from wanted_jjh.db.session import engine
from wanted_jjh.enums import LanguageCode
from wanted_jjh.models.company import Company
from wanted_jjh.models.company import CompanyName
from wanted_jjh.models.company_tag import CompanyTag
from wanted_jjh.models.company_tag import CompanyTagName


def setup_init_db():
    DBBase.metadata.drop_all(bind=engine)
    DBBase.metadata.create_all(bind=engine)

    session = Session(bind=engine.connect())

    with open("data/company_tag_sample.csv", "r") as f:
        for row in csv.DictReader(f):
            company_ko = row["company_ko"] or ""
            company_en = row["company_en"] or ""
            company_ja = row["company_ja"] or ""
            ko_tags = [name.strip() for name in row["tag_ko"].split("|")]
            en_tangs = [name.strip() for name in row["tag_en"].split("|")]
            ja_tags = [name.strip() for name in row["tag_ja"].split("|")]

            assert len(ko_tags) == len(en_tangs) == len(ja_tags)

            company = Company()
            company.names.extend(
                [
                    CompanyName(language_code=LanguageCode.ko, name=company_ko),
                    CompanyName(language_code=LanguageCode.en, name=company_en),
                    CompanyName(language_code=LanguageCode.ja, name=company_ja),
                ]
            )

            for ko_tag, en_tag, ja_tag in zip(ko_tags, en_tangs, ja_tags):
                tag = (
                    session.query(CompanyTag)
                    .join(CompanyTagName)
                    .filter(
                        and_(
                            CompanyTagName.language_code == LanguageCode.ko,
                            CompanyTagName.name == ko_tag,
                        )
                        | and_(
                            CompanyTagName.language_code == LanguageCode.en,
                            CompanyTagName.name == en_tag,
                        )
                        | and_(
                            CompanyTagName.language_code == LanguageCode.tw,
                            CompanyTagName.name == ja_tag,
                        )
                    )
                    .first()
                )

                if not tag:
                    tag = CompanyTag()
                    tag.names.extend(
                        [
                            CompanyTagName(language_code=LanguageCode.ko, name=ko_tag),
                            CompanyTagName(language_code=LanguageCode.en, name=en_tag),
                            CompanyTagName(language_code=LanguageCode.ja, name=ja_tag),
                        ]
                    )

                company.tags.append(tag)

                session.add(company)
                session.commit()


if __name__ == "__main__":
    setup_init_db()
