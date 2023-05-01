from sqlalchemy.orm.session import Session
from sqlalchemy.sql._elements_constructors import text

def ping_db(db: Session):
    '''
    Perform a simple query to make sure we can connect to the database
    '''
    
    result = db.execute(text("SELECT 1"))
    if result.cursor.arraysize == 1:
        return True
    return False