from pydantic import BaseModel


class CompanySearchSchema(BaseModel):
    company_name: str


class CompanySchema(BaseModel):
    company_name: str
    tags: list[str]


class LanguageCodeSchema(BaseModel):
    ko: str | None = None
    en: str | None = None
    ja: str | None = None
    tw: str | None = None


class Tag(BaseModel):
    tag_name: LanguageCodeSchema


class CompanyCreateSchema(BaseModel):
    company_name: LanguageCodeSchema
    tags: list[Tag]


class CompanyTagUpdateSchema(BaseModel):
    tag_name: LanguageCodeSchema
