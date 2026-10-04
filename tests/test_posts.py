def test_create_post(client, authorized_client):
    """
    Check that an authenticated user can create a post.

    A post should be associated with the currently logged-in user.
    We verify the response status and the submitted post data.

    `authorized_client` is a fixture you can create later.
    It should return a TestClient that includes a valid JWT token.
    """
    post_data = {
        "title": "Test post",
        "content": "This is a test post",
        "published": True,
        "rating": 5
    }

    response = authorized_client.post("/posts/", json=post_data)

    assert response.status_code == 201
    assert response.json()["title"] == post_data["title"]
    assert response.json()["content"] == post_data["content"]


def test_create_post_unauthorized(client):
    """
    Check that a user cannot create a post without logging in.

    The request has no Authorization header.
    A protected endpoint should reject it with 401 or 403,
    depending on how your authentication dependency is configured.
    """
    post_data = {
        "title": "Unauthorized post",
        "content": "This should not be created",
        "published": True,
        "rating": 5
    }

    response = client.post("/posts/", json=post_data)

    assert response.status_code in [401, 403]

def test_get_all_posts(authorized_client):
    """
    Check that the GET posts endpoint responds successfully.

    This is a basic endpoint test. It does not assume the database
    is empty, because other tests may create posts.
    """
    response = authorized_client.get("/posts/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_post(client, authorized_client):
    """
    Create a post, then retrieve it using its ID.

    This checks both the create and read paths together.
    """
    post_data = {
        "title": "Single post",
        "content": "Testing retrieval",
        "published": True,
        "rating": 5
    }

    create_response = authorized_client.post("/posts/", json=post_data)
    assert create_response.status_code == 201

    post_id = create_response.json()["id"]
    response = authorized_client.get(f"/posts/{post_id}")

    response_data = response.json()

    assert response.status_code == 200
    assert response_data["post"]["id"] == post_id
    assert response_data["post"]["title"] == post_data["title"]
    assert response_data["post"]["content"] == post_data["content"]
    assert response_data["votes"] == 0

def test_get_nonexistent_post(authorized_client):
    """
    Check that requesting a post that does not exist returns 404.
    """
    
    response = authorized_client.get("/posts/999999")

    assert response.status_code == 404


def test_delete_post(client, authorized_client):
    """
    Check that the owner can delete their own post.

    After deletion, requesting the same post should return 404.
    """
    post_data = {
        "title": "Post to delete",
        "content": "This post will be deleted",
        "published": True,
        "rating": 5
    }

    create_response = authorized_client.post("/posts/", json=post_data)
    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    delete_response = authorized_client.delete(f"/posts/{post_id}")
    assert delete_response.status_code in [200, 204]

    get_response = client.get(f"/posts/{post_id}")
    assert get_response.status_code == 404


def test_update_post(client, authorized_client):
    """
    Check that the owner can update their post.

    We create a post, send an update request, and verify that
    the returned data contains the updated values.
    """
    post_data = {
        "title": "Original title",
        "content": "Original content",
        "published": True,
        "rating": 5
    }

    create_response = authorized_client.post("/posts/", json=post_data)
    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    updated_data = {
        "title": "Updated title",
        "content": "Updated content",
        "published": False,
        "rating": 4
    }

    response = authorized_client.put(
        f"/posts/{post_id}",
        json=updated_data
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["content"] == "Updated content"