from app.models.poi import POI
from app.models.user import User
from app.utils.security import get_password_hash


def _create_user(db_session, username, is_admin=False):
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        is_admin=is_admin,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _get_token(client, username):
    response = client.post("/api/v1/auth/login", data={
        "username": username,
        "password": "testpass123",
    })
    return response.json()["access_token"]


def _create_pois(db_session):
    pois = [
        POI(name="故宫", address="北京市东城区", type="古建筑", batch="第一批",
            lon=116.397, lat=39.916, geom="SRID=4326;POINT(116.397 39.916)"),
        POI(name="天坛", address="北京市东城区", type="古建筑", batch="第一批",
            lon=116.407, lat=39.883, geom="SRID=4326;POINT(116.407 39.883)"),
        POI(name="兵马俑", address="陕西省西安市", type="古遗址", batch="第一批",
            lon=109.278, lat=34.384, geom="SRID=4326;POINT(109.278 34.384)"),
    ]
    for poi in pois:
        db_session.add(poi)
    db_session.commit()
    for poi in pois:
        db_session.refresh(poi)
    return pois


def test_list_pois(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_pois_filter_by_name(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/", params={"name": "故宫"},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "故宫"


def test_list_pois_filter_by_type(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/", params={"type": "古建筑"},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_pois_filter_by_province(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/", params={"province": "北京"},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_pois_bbox(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/", params={
        "min_lon": 116.0, "max_lon": 117.0,
        "min_lat": 39.0, "max_lat": 40.0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_pois_radius(client, db_session):
    _create_user(db_session, "user1")
    pois = _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/", params={
        "center_lon": 116.4,
        "center_lat": 39.9,
        "radius_km": 10,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    names = [p["name"] for p in data]
    assert "故宫" in names
    assert "天坛" in names
    assert "兵马俑" not in names


def test_list_pois_pagination(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/", params={"limit": 2, "skip": 0},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/api/v1/pois/", params={"limit": 2, "skip": 2},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_poi(client, db_session):
    _create_user(db_session, "user1")
    pois = _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get(f"/api/v1/pois/{pois[0].id}",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "故宫"


def test_get_poi_not_found(client, db_session):
    _create_user(db_session, "user1")
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["error_code"] == "POI_001"


def test_list_types(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/types/list",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "古建筑" in data
    assert "古遗址" in data


def test_list_batches(client, db_session):
    _create_user(db_session, "user1")
    _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.get("/api/v1/pois/batches/list",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "第一批" in data


def test_create_poi_admin(client, db_session):
    _create_user(db_session, "admin1", is_admin=True)
    token = _get_token(client, "admin1")

    response = client.post("/api/v1/pois/", json={
        "name": "测试文物",
        "address": "北京市",
        "type": "古建筑",
        "lon": 116.4,
        "lat": 39.9,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "测试文物"


def test_create_poi_non_admin(client, db_session):
    _create_user(db_session, "user1")
    token = _get_token(client, "user1")

    response = client.post("/api/v1/pois/", json={
        "name": "测试文物",
        "address": "北京市",
        "type": "古建筑",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["error_code"] == "AUTH_002"


def test_update_poi(client, db_session):
    _create_user(db_session, "admin1", is_admin=True)
    pois = _create_pois(db_session)
    token = _get_token(client, "admin1")

    response = client.put(f"/api/v1/pois/{pois[0].id}", json={
        "name": "故宫博物院",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "故宫博物院"


def test_update_poi_not_found(client, db_session):
    _create_user(db_session, "admin1", is_admin=True)
    token = _get_token(client, "admin1")

    response = client.put("/api/v1/pois/999", json={
        "name": "不存在",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["error_code"] == "POI_001"


def test_delete_poi(client, db_session):
    _create_user(db_session, "admin1", is_admin=True)
    pois = _create_pois(db_session)
    token = _get_token(client, "admin1")

    response = client.delete(f"/api/v1/pois/{pois[0].id}",
                             headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    response = client.get(f"/api/v1/pois/{pois[0].id}",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_delete_poi_non_admin(client, db_session):
    _create_user(db_session, "user1")
    pois = _create_pois(db_session)
    token = _get_token(client, "user1")

    response = client.delete(f"/api/v1/pois/{pois[0].id}",
                             headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["error_code"] == "AUTH_002"
