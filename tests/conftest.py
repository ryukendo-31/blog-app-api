import os
from dotenv import load_dotenv
import pytest 
from fastapi.testclient import TestClient


load_dotenv(".env.test", override = True)

os.environ["DATABASE_HOSTNAME"] = os.getenv("DATABASE_HOSTNAME")
os.environ["DATABASE_PORT"] = os.getenv("DATABASE_PORT")
os.environ["DATABASE_NAME"] = os.getenv("DATABASE_NAME")
os.environ["DATABASE_USERNAME"] = os.getenv("DATABASE_USERNAME")
os.environ["DATABASE_PASSWORD"] = os.getenv("DATABASE_PASSWORD")
from app import models
from app.database import engine, sessionLocal, get_db
from app.main import app

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

# @pytest.fixture(autouse=True)
# def clean_database():
#     yield
#     with engine.begin() as conn:
#         for table in reversed(models.Base.metadata.sorted_tables):
#             conn.execute(table.delete())

@pytest.fixture
def db_transaction():
    connection = engine.connect()
    transaction = connection.begin()

    yield connection

    transaction.rollback()
    connection.close()

@pytest.fixture
def db_session(db_transaction):
    db = sessionLocal(
        bind=db_transaction,
        join_transaction_mode="create_savepoint"
    )

    yield db

    db.close()


@pytest.fixture
def authorized_client(client):
    """
    Create a test user, log in, and return an authenticated client.

    Any test that requests this fixture will automatically receive
    a client with a valid JWT token in its Authorization header.
    """

    # 1. Create a user for this test.
    user_data = {
        "email": "authorized@example.com",
        "password": "testpassword"
    }

    create_response = client.post("/users/", json=user_data)
    assert create_response.status_code == 201

    # 2. Log in using OAuth2 form data.
    # OAuth2PasswordRequestForm expects the email in "username".
    login_response = client.post(
        "/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 200

    # 3. Extract the JWT access token.
    token = login_response.json()["access_token"]

    # 4. Attach the token to every request made by this client.
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    # 5. Return the now-authenticated client.
    return client
