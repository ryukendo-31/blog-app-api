def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["message"] == "hello from docker"


def test_create_user(client):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    res = client.post("/users/", json=user_data)
    print(res.json())
    assert res.status_code == 201
    assert res.json()["email"] == "test@example.com"
    assert "password" not in res.json()

def test_user_isolation(client):
    res = client.get("/users/999999")
    assert res.status_code == 404
