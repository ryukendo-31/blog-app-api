def test_root(client):
    res = client.get("/")
    print(res.json().get('message'))
    assert res.status_code == 200
    assert res.json()["message"] == "hello from docker"