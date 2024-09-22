from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Table

from wanted_jjh.db.session import DBBase

association_company_and_company_tag = Table(
    "association_company_and_company_tag",
    DBBase.metadata,
    Column("company_id", Integer, ForeignKey("companies.id")),
    Column("company_tag_id", Integer, ForeignKey("company_tags.id")),
)


class CompanyTag(DBBase):
    __tablename__ = "company_tags"

    id = Column(Integer, primary_key=True, index=True)

    companies = relationship(
        "Company", secondary=association_company_and_company_tag, back_populates="tags"
    )

    names = relationship("CompanyTagName", back_populates="tag")

    def get_name(self, language_code="en"):
        translation_name = next(
            translation.name
            for translation in self.names
            if translation.language_code == language_code
        )
        return translation_name


class CompanyTagName(DBBase):
    __tablename__ = "company_tag_name_translations"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("company_tags.id"))
    language_code = Column(String(2))  # e.g., 'ko', 'en', 'ja'
    name = Column(String(100))

    tag = relationship("CompanyTag", back_populates="names")
