from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyDTO:
    name: str
    tag_names: list[str] | None = None


@dataclass(frozen=True)
class TagDTO:
    ko_name: str | None = None
    en_name: str | None = None
    ja_name: str | None = None
    tw_name: str | None = None


@dataclass(frozen=True)
class CreateCompanyDTO:
    ko_name: str
    en_name: str
    tw_name: str
    tags: list[TagDTO]


@dataclass(frozen=True)
class AppendCompanyTagDTO:
    tag_ko_name: str
    tag_en_name: str
    tag_ja_name: str
