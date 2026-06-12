
def test_read_user(client, auth_headers):
    response = client.get("/user/me", headers=auth_headers)

    assert response.status_code == 200

def test_read_user_unauthenticated(client):
    response = client.get("/user/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_user_change_password(client, auth_headers):
    response = client.put("/user/change_password", headers=auth_headers, json={
        "password": "test_password",
        "new_password": "new_test_password",
        "confirm_new_password": "new_test_password",
    })

    assert response.status_code == 204

    login_response = client.post("/auth/token", data={
            "username": "test@example.com",
            "password": "new_test_password",
        },
    )

    assert login_response.status_code == 200

    old_login = client.post("/auth/token", data={
            "username": "test@example.com",
            "password": "test_password",
        },
    )

    assert old_login.status_code == 400

def test_user_change_password_unauthenticated(client):
    response = client.put("/user/change_password", json={
        "password": "test_password",
        "new_password": "new_test_password",
        "confirm_new_password": "new_test_password",
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_user_change_password_wrong_password(client, auth_headers):
    response = client.put("/user/change_password", headers=auth_headers, json={
        "password": "wrong_password",
        "new_password": "new_test_password",
        "confirm_new_password": "new_test_password",
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Wrong password."

def test_user_change_password_no_matching_password(client, auth_headers):
    response = client.put("/user/change_password", headers=auth_headers, json={
        "password": "test_password",
        "new_password": "new_test_password",
        "confirm_new_password": "new_test_password1",
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match."

