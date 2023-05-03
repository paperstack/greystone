from sqlalchemy.orm.session import Session
from app import schemas
from app.models import User

def create_user(db: Session, user: schemas.UserCreate):
    _user = User(**user.dict())
    db.add(_user)
    db.commit()
    db.refresh(_user)
    return _user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email==email).first()

def get_user_loans(db: Session, user: User):
    """
    Returns all the loans associated with a given user
    """
    return user.loans