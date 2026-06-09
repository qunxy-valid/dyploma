from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "python-devops-lifecycle",
    }


def test_dashboard_page_available(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Python DevOps Lifecycle" in response.text


def test_create_and_list_quality_issue(client: TestClient) -> None:
    payload = {
        "title": "Missing regression test for authentication",
        "service": "identity",
        "severity": "high",
    }

    create_response = client.post("/issues", json=payload)
    list_response = client.get("/issues")

    assert create_response.status_code == 201
    assert create_response.json() == {
        "id": 1,
        "status": "open",
        **payload,
    }
    assert list_response.status_code == 200
    assert list_response.json() == [create_response.json()]


def test_quality_summary_counts_open_and_resolved_issues(
    client: TestClient,
) -> None:
    client.post(
        "/issues",
        json={
            "title": "Code path has no unit tests",
            "service": "orders",
            "severity": "medium",
        },
    )
    client.post(
        "/issues",
        json={
            "title": "Critical production error is not covered",
            "service": "payments",
            "severity": "critical",
        },
    )

    resolve_response = client.patch("/issues/1/resolve")
    summary_response = client.get("/quality-summary")

    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == "resolved"
    assert summary_response.status_code == 200
    assert summary_response.json() == {
        "total_issues": 2,
        "open_issues": 1,
        "resolved_issues": 1,
        "reliability_score": 75.0,
    }


def test_resolve_unknown_issue_returns_404(client: TestClient) -> None:
    response = client.patch("/issues/999/resolve")

    assert response.status_code == 404
    assert response.json() == {"detail": "Quality issue not found"}


def test_seed_demo_issues(client: TestClient) -> None:
    seed_response = client.post("/demo/seed")
    summary_response = client.get("/quality-summary")

    assert seed_response.status_code == 200
    assert len(seed_response.json()) == 3
    assert summary_response.json() == {
        "total_issues": 3,
        "open_issues": 2,
        "resolved_issues": 1,
        "reliability_score": 60.0,
    }


def test_demo_pipeline_report(client: TestClient) -> None:
    response = client.get("/demo/pipeline")
    data = response.json()

    assert response.status_code == 200
    assert data["passed"] is True
    assert data["coverage_percent"] == 96.0
    assert "def test_" in data["sample_test_code"]
    assert [stage["command"] for stage in data["stages"]] == [
        "ruff format --check .",
        "ruff check .",
        "mypy app",
        "pytest",
        "docker build -t python-devops-lifecycle .",
    ]
