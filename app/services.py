from typing import ClassVar

from app.schemas import (
    DemoPipelineReport,
    IssueStatus,
    PipelineStage,
    PipelineStageStatus,
    QualityIssue,
    QualityIssueCreate,
    QualitySummary,
    Severity,
)

SAMPLE_CODE = '''\
def calculate_reliability_score(
    open_issues: int,
    critical_issues: int,
) -> float:
    """Return a simple software reliability score from 0 to 100."""
    penalty = open_issues * 4 + critical_issues * 15
    return max(0.0, 100.0 - penalty)
'''

SAMPLE_TEST_CODE = """\
def test_calculate_reliability_score_for_stable_release() -> None:
    score = calculate_reliability_score(open_issues=2, critical_issues=0)

    assert score == 92.0


def test_calculate_reliability_score_has_lower_bound() -> None:
    score = calculate_reliability_score(open_issues=40, critical_issues=5)

    assert score == 0.0
"""


class IssueRepository:
    severity_weights: ClassVar[dict[Severity, int]] = {
        Severity.low: 4,
        Severity.medium: 8,
        Severity.high: 15,
        Severity.critical: 25,
    }

    def __init__(self) -> None:
        self._issues: dict[int, QualityIssue] = {}
        self._next_id = 1

    def create(self, payload: QualityIssueCreate) -> QualityIssue:
        issue = QualityIssue(
            id=self._next_id,
            title=payload.title,
            service=payload.service,
            severity=payload.severity,
            status=IssueStatus.open,
        )
        self._issues[issue.id] = issue
        self._next_id += 1
        return issue

    def list_all(self) -> list[QualityIssue]:
        return [issue.model_copy() for issue in self._issues.values()]

    def resolve(self, issue_id: int) -> QualityIssue | None:
        issue = self._issues.get(issue_id)
        if issue is None:
            return None

        resolved_issue = issue.model_copy(update={"status": IssueStatus.resolved})
        self._issues[issue_id] = resolved_issue
        return resolved_issue

    def seed_demo(self) -> list[QualityIssue]:
        if self._issues:
            return self.list_all()

        self.create(
            QualityIssueCreate(
                title="Missing regression test for authentication",
                service="identity",
                severity=Severity.high,
            )
        )
        self.create(
            QualityIssueCreate(
                title="Docker image size should be optimized",
                service="deployment",
                severity=Severity.low,
            )
        )
        self.create(
            QualityIssueCreate(
                title="Critical payment flow has no negative tests",
                service="payments",
                severity=Severity.critical,
            )
        )
        self.resolve(2)

        return self.list_all()

    def summary(self) -> QualitySummary:
        issues = self.list_all()
        open_issues = [issue for issue in issues if issue.status is IssueStatus.open]
        resolved_issues = [
            issue for issue in issues if issue.status is IssueStatus.resolved
        ]
        penalty = sum(self.severity_weights[issue.severity] for issue in open_issues)

        return QualitySummary(
            total_issues=len(issues),
            open_issues=len(open_issues),
            resolved_issues=len(resolved_issues),
            reliability_score=max(0.0, round(100.0 - penalty, 2)),
        )


def build_demo_pipeline_report(summary: QualitySummary) -> DemoPipelineReport:
    stages = [
        PipelineStage(
            name="Format",
            command="ruff format --check .",
            status=PipelineStageStatus.passed,
            duration_ms=310,
        ),
        PipelineStage(
            name="Lint",
            command="ruff check .",
            status=PipelineStageStatus.passed,
            duration_ms=420,
        ),
        PipelineStage(
            name="Types",
            command="mypy app",
            status=PipelineStageStatus.passed,
            duration_ms=1170,
        ),
        PipelineStage(
            name="Tests",
            command="pytest",
            status=PipelineStageStatus.passed,
            duration_ms=890,
        ),
        PipelineStage(
            name="Docker",
            command="docker build -t python-devops-lifecycle .",
            status=PipelineStageStatus.passed,
            duration_ms=2640,
        ),
    ]

    coverage = (
        96.0 if summary.open_issues == 0 else max(72.0, 96.0 - summary.open_issues * 6)
    )

    return DemoPipelineReport(
        branch="main",
        commit="demo-7f3a2c1",
        passed=all(stage.status is PipelineStageStatus.passed for stage in stages),
        coverage_percent=round(coverage, 1),
        tested_files=["app/main.py", "app/services.py", "tests/test_main.py"],
        stages=stages,
        sample_code=SAMPLE_CODE,
        sample_test_code=SAMPLE_TEST_CODE,
    )
