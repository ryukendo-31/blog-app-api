def test_vote_on_post(client, authorized_client):
    """
    Check that an authenticated user can vote on a post.

    We first create a post, then vote on it.
    The response should indicate that the vote was successful.
    """
    post_data = {
        "title": "Post to vote on",
        "content": "Vote testing",
        "published": True,
        "rating": 5
    }

    post_response = authorized_client.post("/posts/", json=post_data)
    assert post_response.status_code == 201

    post_id = post_response.json()["id"]

    vote_response = authorized_client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 1}
    )

    assert vote_response.status_code in [200, 201]


def test_vote_unauthorized(client):
    """
    A user who is not logged in should not be able to vote.
    """
    response = client.post(
        "/vote/",
        json={"post_id": 1, "dir": 1}
    )

    assert response.status_code in [401, 403]


def test_vote_nonexistent_post(authorized_client):
    """
    A user should not be able to vote on a post that does not exist.
    """
    response = authorized_client.post(
        "/vote/",
        json={"post_id": 999999, "dir": 1}
    )

    assert response.status_code == 404


def test_remove_vote(client, authorized_client):
    """
    Check that a user can remove their vote.

    First cast a vote, then send dir=0 for the same post.
    """
    post_data = {
        "title": "Post for vote removal",
        "content": "Testing vote removal",
        "published": True,
        "rating": 5
    }

    post_response = authorized_client.post("/posts/", json=post_data)
    assert post_response.status_code == 201

    post_id = post_response.json()["id"]

    # Cast the vote.
    vote_response = authorized_client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 1}
    )
    assert vote_response.status_code in [200, 201]

    # Remove the vote.
    remove_response = authorized_client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 0}
    )
    assert remove_response.status_code in [200, 201]