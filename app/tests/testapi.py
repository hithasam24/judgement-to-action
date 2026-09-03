import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dashboard_endpoint():
    response = client.get("/api/v1/dashboard/verified")
    assert response.status_code == 200
    assert "dashboard_data" in response.json()

def test_pending_reviews_endpoint():
    response = client.get("/api/v1/review/pending")
    assert response.status_code == 200
    assert "pending_cases" in response.json()