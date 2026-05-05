import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a fresh TestClient for each test."""
    return TestClient(app)


# ============================================================================
# GET /activities Tests
# ============================================================================

class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200_status(self, client):
        """Test that GET /activities returns a 200 status code."""
        # Arrange
        expected_status = 200

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == expected_status

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all 9 activities."""
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert len(activities) == expected_activity_count

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has the required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields

    def test_get_activities_chess_club_exists(self, client):
        """Test that Chess Club activity is in the dictionary."""
        # Arrange
        expected_activity_name = "Chess Club"

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert expected_activity_name in activities.keys()

    def test_get_activities_response_is_json_dict(self, client):
        """Test that response is a JSON dictionary."""
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert isinstance(activities, dict)


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

class TestSignupActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid_activity_returns_200(self, client):
        """Test that signing up for a valid activity returns 200 status."""
        # Arrange
        activity_name = "Chess Club"
        email = "student1@school.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

    def test_signup_adds_participant_to_activity(self, client):
        """Test that participant is added to activity's participants list."""
        # Arrange
        activity_name = "Chess Club"
        email = "student2@school.com"

        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_signup_returns_400(self, client):
        """Test that signing up twice returns 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = "student3@school.com"

        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student4@school.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

    def test_signup_missing_email_returns_422(self, client):
        """Test that missing email parameter returns 422 validation error."""
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422

    def test_signup_returns_success_message(self, client):
        """Test that successful signup returns a success message."""
        # Arrange
        activity_name = "Programming Class"
        email = "student5@school.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert "success" in response.json() or "message" in response.json()

    def test_signup_multiple_students_to_same_activity(self, client):
        """Test that multiple students can sign up for the same activity."""
        # Arrange
        activity_name = "Basketball Team"
        email1 = "student6@school.com"
        email2 = "student7@school.com"

        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


# ============================================================================
# DELETE /activities/{activity_name}/unregister Tests
# ============================================================================

class TestUnregisterActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_valid_signup_returns_200(self, client):
        """Test that unregistering a valid signup returns 200 status."""
        # Arrange
        activity_name = "Art Club"
        email = "student8@school.com"
        # Prerequisite: Sign up first
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

    def test_unregister_removes_participant_from_activity(self, client):
        """Test that participant is removed from activity's participants list."""
        # Arrange
        activity_name = "Drama Club"
        email = "student9@school.com"
        # Prerequisite: Sign up first
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student10@school.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_400(self, client):
        """Test that unregistering when not signed up returns 400 error."""
        # Arrange
        activity_name = "Debate Club"
        email = "student11@school.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400

    def test_unregister_missing_email_returns_422(self, client):
        """Test that missing email parameter returns 422 validation error."""
        # Arrange
        activity_name = "Science Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister")

        # Assert
        assert response.status_code == 422

    def test_unregister_returns_success_message(self, client):
        """Test that successful unregister returns a success message."""
        # Arrange
        activity_name = "Soccer Club"
        email = "student12@school.com"
        # Prerequisite: Sign up first
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert "success" in response.json() or "message" in response.json()

    def test_unregister_signup_unregister_workflow(self, client):
        """Test complete workflow: signup, verify, unregister, verify removal."""
        # Arrange
        activity_name = "Gym Class"
        email = "student13@school.com"

        # Act - Sign up
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Verify participant added
        response_get_1 = client.get("/activities")
        activities_1 = response_get_1.json()

        # Act - Unregister
        response_unregister = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Act - Verify participant removed
        response_get_2 = client.get("/activities")
        activities_2 = response_get_2.json()

        # Assert
        assert response_signup.status_code == 200
        assert email in activities_1[activity_name]["participants"]
        assert response_unregister.status_code == 200
        assert email not in activities_2[activity_name]["participants"]

    def test_unregister_one_student_keeps_others_signed_up(self, client):
        """Test that unregistering one student doesn't affect others."""
        # Arrange
        activity_name = "Programming Class"
        email1 = "student14@school.com"
        email2 = "student15@school.com"
        # Prerequisite: Sign up both students
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})

        # Act
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email1})
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email1 not in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
