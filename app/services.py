from typing import ClassVar

from app.schemas import (
    IssueStatus,
    QualityIssue,
    QualityIssueCreate,
    QualitySummary,
    Severity,
)


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
