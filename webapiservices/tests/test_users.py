def _register_and_login(client, username="testuser"):
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    response = client.post("/api/v1/auth/login", data={
        "username": username,
        "password": "testpass123",
    })
    return response.json()["access_token"]


def test_get_me(client):
    token = _register_and_login(client)
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["is_admin"] is False


def test_update_me(client):
    token = _register_and_login(client)
    response = client.put("/api/v1/users/me", json={
        "full_name": "Updated Name",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


def test_generate_api_key(client):
    token = _register_and_login(client)
    response = client.post("/api/v1/users/api-key", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "api_key" in response.json()


def test_api_key_auth(client):
    token = _register_and_login(client)
    api_key_resp = client.post("/api/v1/users/api-key", headers={"Authorization": f"Bearer {token}"})
    api_key = api_key_resp.json()["api_key"]

    response = client.get("/api/v1/pois/types/list", params={"api_key": api_key})
    assert response.status_code == 200
