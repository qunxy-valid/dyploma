from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import (
    DemoPipelineReport,
    QualityIssue,
    QualityIssueCreate,
    QualitySummary,
)
from app.services import IssueRepository, build_demo_pipeline_report

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"


def create_app(repository: IssueRepository | None = None) -> FastAPI:
    app = FastAPI(
        title="Python DevOps Lifecycle API",
        description="API for tracking code quality issues in a CI/CD workflow.",
        version="1.0.0",
    )
    issue_repository = repository or IssueRepository()
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    def get_repository() -> IssueRepository:
        return issue_repository

    @app.get("/", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

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

    @app.post("/demo/seed", response_model=list[QualityIssue])
    def seed_demo_issues(
        repository: Annotated[IssueRepository, Depends(get_repository)],
    ) -> list[QualityIssue]:
        return repository.seed_demo()

    @app.get("/demo/pipeline", response_model=DemoPipelineReport)
    def demo_pipeline(
        repository: Annotated[IssueRepository, Depends(get_repository)],
    ) -> DemoPipelineReport:
        return build_demo_pipeline_report(repository.summary())

    return app


app = create_app()
