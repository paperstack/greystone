import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from app.logic.ping_db import ping_db
from app.schemas import UserCreate
from app.logic.user import create_user

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
    
def test_user_create(db):
    user_input = UserCreate(**{"first_name": "Grey", "last_name": "Stone", "email": "greystone@greystone.com"})
    
    user = create_user(db=db, user=user_input)
    assert  user_input.first_name == user.first_name
    assert  user_input.last_name == user.last_name
    assert  user_input.email == user.email
    assert  user.id > 0