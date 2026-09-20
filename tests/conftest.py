import os
from dotenv import load_dotenv
import pytest 
from fastapi.testclient import TestClient

load_dotenv(".env.test")

os.environ["DATABASE_HOSTNAME"] = os.getenv("DATABASE_HOSTNAME")
os.environ["DATABASE_PORT"] = os.getenv("DATABASE_PORT")
os.environ["DATABASE_NAME"] = os.getenv("DATABASE_NAME")
os.environ["DATABASE_USERNAME"] = os.getenv("DATABASE_USERNAME")
os.environ["DATABASE_PASSWORD"] = os.getenv("DATABASE_PASSWORD")


from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
    