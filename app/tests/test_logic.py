import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from app.logic.ping_db import ping_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        
        
def test_ping_db(db):
    assert True == ping_db(db=db)