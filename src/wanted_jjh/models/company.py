from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from wanted_jjh.db.session import DBBase
from wanted_jjh.models.company_tag import association_company_and_company_tag


class Company(DBBase):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    names = relationship("CompanyName", back_populates="company")

    tags = relationship(
        "CompanyTag",
        secondary=association_company_and_company_tag,
        back_populates="companies",
    )

    def get_name(self, language_code="en") -> str:
        translation_name = next(
            (
                translation.name
                for translation in self.names
                if translation.language_code == language_code
            ),
            "",
        )
        return translation_name


class CompanyName(DBBase):
    __tablename__ = "company_name_translations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    language_code = Column(String(2))  # e.g., 'ko', 'en', 'ja'
    name = Column(String(100))

    company = relationship("Company", back_populates="names")
