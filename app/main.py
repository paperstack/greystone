from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app import models
from app.database import engine, SessionLocal 
from app.logic.ping_db import ping_db

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

