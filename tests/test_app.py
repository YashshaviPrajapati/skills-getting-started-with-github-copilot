from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict before/after each test."""
    original = deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities.clear()
        app_module.activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity to exist
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    email = "testuser@example.com"
    activity_name = "Math Club"

    # ensure participant not present
    assert email not in app_module.activities[activity_name]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities[activity_name]["participants"]

    # Remove
    resp = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert resp.status_code == 200
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    resp = client.delete("/activities/Math%20Club/participants?email=nonexistent%40example.com")
    assert resp.status_code == 404
