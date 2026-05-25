def test_register(client):
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_username(client):
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test1@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test2@example.com",
        "password": "testpass123",
        "full_name": "Test User 2",
    })
    assert response.status_code == 400
    assert response.json()["error_code"] == "AUTH_004"


def test_register_duplicate_email(client):
    client.post("/api/v1/auth/register", json={
        "username": "user1",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    response = client.post("/api/v1/auth/register", json={
        "username": "user2",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User 2",
    })
    assert response.status_code == 400
    assert response.json()["error_code"] == "AUTH_005"


def test_login(client):
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "wrongpass",
    })
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTH_001"
