from app.core.security import ALGORITHM, SECRET_KEY
import jwt

REGISTER_DATA = {
    "email": "test@example.com",
    "full_name": "test mcTesty",
    "password": "123456",
    "confirm_password": "123456",
}

def test_register_user(client):
    response = client.post("/auth/register", json=REGISTER_DATA)

    assert response.status_code == 201
    assert "id" in response.json()

def test_register_user_exists(client, mock_user) -> None:
    response = client.post("/auth/register", json=REGISTER_DATA)

    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this email already exists."

def test_register_user_no_matching_passwords(client) -> None:
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "full_name": "test mcTesty",
        "password": "123456",
        "confirm_password": "1234567",
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match."

def test_login_for_access_token(client, mock_user) -> None:
    # We send form_data instead of json
    response = client.post("/auth/token", data={
        "username": mock_user.email,
        "password": "test_password"
    })

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    payload = jwt.decode(
            response.json()["access_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert payload["sub"] == str(mock_user.id)

def test_login_for_access_token_no_user(client) -> None:
    # We send form_data instead of json
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "test_password"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password."

def test_login_for_access_token_wrong_password(client) -> None:
    # We send form_data instead of json
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "1234"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password."

def test_login_for_access_token_user_inactive(client, mock_user, session) -> None:
    mock_user.is_active = False
    session.add(mock_user)
    session.flush()

    # We send form_data instead of json
    response = client.post("/auth/token", data={
        "username": mock_user.email,
        "password": "test_password"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user."
