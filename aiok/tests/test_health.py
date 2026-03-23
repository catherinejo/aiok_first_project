"""Smoke tests for HTTP surface."""

from fastapi.testclient import TestClient

from aiok.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert "version" in body
