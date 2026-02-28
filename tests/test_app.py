import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_seeded_data(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in payload
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_adds_new_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"
    endpoint = f"/activities/Chess Club/signup?email={email}"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"
    endpoint = f"/activities/Chess Club/signup?email={email}"

    # Act
    response = client.post(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 409
    assert payload["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    endpoint = "/activities/Unknown Activity/signup?email=student@mergington.edu"

    # Act
    response = client.post(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_unregister_removes_existing_participant(client):
    # Arrange
    email = "michael@mergington.edu"
    endpoint = f"/activities/Chess Club/signup?email={email}"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client):
    # Arrange
    endpoint = "/activities/Chess Club/signup?email=missing@mergington.edu"

    # Act
    response = client.delete(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Participant not found"
