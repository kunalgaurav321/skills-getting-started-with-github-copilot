import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Original activities data for resetting
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

@pytest.fixture
def client():
    """Fixture to provide a TestClient instance."""
    return TestClient(app, follow_redirects=False)

@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset the activities data before each test."""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))

def test_get_root(client):
    """Test GET / redirects to static index.html."""
    # Arrange - no special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test GET /activities returns all activities data."""
    # Arrange - data is reset by fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]

def test_signup_success(client):
    """Test POST /activities/{activity_name}/signup with valid data."""
    # Arrange
    activity_name = "Chess Club"
    email = "new@student.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in activities[activity_name]["participants"]

def test_signup_activity_not_found(client):
    """Test POST /activities/{activity_name}/signup with invalid activity."""
    # Arrange
    activity_name = "NonExistent"
    email = "test@test.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_signup_duplicate(client):
    """Test POST /activities/{activity_name}/signup allows duplicates."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert len(activities[activity_name]["participants"]) == initial_count + 1
    assert activities[activity_name]["participants"].count(email) == 2

def test_delete_success(client):
    """Test DELETE /activities/{activity_name}/signup with valid data."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email not in activities[activity_name]["participants"]

def test_delete_activity_not_found(client):
    """Test DELETE /activities/{activity_name}/signup with invalid activity."""
    # Arrange
    activity_name = "NonExistent"
    email = "test@test.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_delete_participant_not_found(client):
    """Test DELETE /activities/{activity_name}/signup with email not in participants."""
    # Arrange
    activity_name = "Chess Club"
    email = "not@here.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"