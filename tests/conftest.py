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

from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

from app import models
from app.database import engine

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_database():
    yield
    with engine.begin() as conn:
        for table in reversed(models.Base.metadata.sorted_tables):
            conn.execute(table.delete())