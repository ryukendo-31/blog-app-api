def test_login(client):
    """
    Check the complete login flow.

    First create a user, then log in using the same credentials.
    A successful login should return a JWT access token.
    """
    user_data = {
        "email": "login@example.com",
        "password": "testpassword"
    }

    create_response = client.post("/users/", json=user_data)
    assert create_response.status_code == 201

    # OAuth2PasswordRequestForm expects form data.
    # In this tutorial, the username field contains the email.
    login_response = client.post(
        "/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    """
    A correct email with an incorrect password should be rejected.
    """
    user_data = {
        "email": "wrongpassword@example.com",
        "password": "correctpassword"
    }

    client.post("/users/", json=user_data)

    response = client.post(
        "/login",
        data={
            "username": user_data["email"],
            "password": "incorrectpassword"
        }
    )

    assert response.status_code == 403


def test_login_nonexistent_user(client):
    """
    Attempt to log in with an email that was never registered.
    The API should reject the login.
    """
    response = client.post(
        "/login",
        data={
            "username": "doesnotexist@example.com",
            "password": "somepassword"
        }
    )

    assert response.status_code == 403