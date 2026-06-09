from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from app.schemas import QualityIssue, QualityIssueCreate, QualitySummary
from app.services import IssueRepository


def create_app(repository: IssueRepository | None = None) -> FastAPI:
    app = FastAPI(
        title="Python DevOps Lifecycle API",
        description="API for tracking code quality issues in a CI/CD workflow.",
        version="1.0.0",
    )
    issue_repository = repository or IssueRepository()

    def get_repository() -> IssueRepository:
        return issue_repository

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "python-devops-lifecycle"}

    @app.post(
        "/issues",
        response_model=QualityIssue,
        status_code=status.HTTP_201_CREATED,
    )
    def create_issue(
        payload: QualityIssueCreate,
        repository: Annotated[IssueRepository, Depends(get_repository)],
    ) -> QualityIssue:
        return repository.create(payload)

    @app.get("/issues", response_model=list[QualityIssue])
    def list_issues(
        repository: Annotated[IssueRepository, Depends(get_repository)],
    ) -> list[QualityIssue]:
        return repository.list_all()

    @app.patch("/issues/{issue_id}/resolve", response_model=QualityIssue)
    def resolve_issue(
        issue_id: int,
        repository: Annotated[IssueRepository, Depends(get_repository)],
    ) -> QualityIssue:
        issue = repository.resolve(issue_id)
        if issue is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quality issue not found",
            )
        return issue

    @app.get("/quality-summary", response_model=QualitySummary)
    def quality_summary(
        repository: Annotated[IssueRepository, Depends(get_repository)],
    ) -> QualitySummary:
        return repository.summary()

    return app


app = create_app()
