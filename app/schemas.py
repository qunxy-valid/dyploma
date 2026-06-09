from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IssueStatus(StrEnum):
    open = "open"
    resolved = "resolved"


class QualityIssueCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    service: str = Field(default="core", min_length=2, max_length=60)
    severity: Severity = Severity.medium


class QualityIssue(QualityIssueCreate):
    id: int
    status: IssueStatus = IssueStatus.open


class QualitySummary(BaseModel):
    total_issues: int = Field(ge=0)
    open_issues: int = Field(ge=0)
    resolved_issues: int = Field(ge=0)
    reliability_score: float = Field(ge=0, le=100)
