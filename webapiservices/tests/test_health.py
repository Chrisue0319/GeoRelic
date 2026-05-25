def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "LBS POI Web API", "docs": "/docs"}


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
