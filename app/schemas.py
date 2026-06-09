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


class PipelineStageStatus(StrEnum):
    passed = "passed"
    failed = "failed"
    skipped = "skipped"


class PipelineStage(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    command: str = Field(min_length=2, max_length=120)
    status: PipelineStageStatus
    duration_ms: int = Field(ge=0)


class DemoPipelineReport(BaseModel):
    branch: str
    commit: str
    passed: bool
    coverage_percent: float = Field(ge=0, le=100)
    tested_files: list[str]
    stages: list[PipelineStage]
    sample_code: str
    sample_test_code: str
