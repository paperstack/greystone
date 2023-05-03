from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app import models, schemas
from app.database import engine, SessionLocal 
from app.logic.ping_db import ping_db
from app.logic.user import get_user_by_email, create_user
from app.logic.loan import create_loan

#TODO: Implement Alembic migrations
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health_check")
def health_check(db: Session = Depends(get_db)):
    if ping_db(db=db):
        return {"Status": "Ok"}
    else:
        raise HTTPException(status_code=400, detail="No Database Connection")

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@app.post("/loans/{email}/", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, email: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=400, detail="No user for loan found")
    return create_loan(db=db, loan=loan, email=email)
