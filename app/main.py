from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app.database import SessionLocal
from app.logic.ping_db import ping_db

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

