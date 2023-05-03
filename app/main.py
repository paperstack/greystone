from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app import models, schemas
from app.database import engine, SessionLocal 
from app.logic.ping_db import ping_db
from app.logic.user import get_user_by_email, create_user, get_user_loans
from app.logic.loan import create_loan, get_loan, share_loan

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

@app.post("/users/", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@app.get("/users/{email}/loans/")
def get_user_loans(email: str, db: Session = Depends(get_db)) -> list[schemas.UserLoan]:
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_user_loans(db=db, user=db_user)

@app.post("/loans/{email}/", response_model=schemas.Loan, status_code=201)
def create_loan(loan: schemas.LoanCreate, email: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="No user for loan found")
    return create_loan(db=db, loan=loan, email=email)

@app.get("/loans/{id}/schedule/")
def get_loan_schedule(id: int, db: Session = Depends(get_db)) -> list[schemas.ScheduleItem]:
    result = get_loan_schedule(db=db, loan_id=id)
    if result is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return result

@app.get("/loans/{id}/month/{month}/")
def get_month_summary(id: int, month: int, db: Session = Depends(get_db)) ->schemas.MonthSummary:
    result = get_month_summary(db=db, loan_id=id, month=month)
    if result is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if result["principal_balance"] is None:
        raise HTTPException(status_code=404, detail="Requested month not found")
    return result

@app.patch("/loans/{id}/share/{email}/")
def share_loan(id: int, email: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=email)
    db_loan = get_loan(db=db, id=id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    share_loan(db=db, user=db_user, loan=db_loan)
