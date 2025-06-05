from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError
import requests


DATABASE_URL = "sqlite:///./db.sqlite"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(255))

Base.metadata.create_all(bind=engine)

class UserModel(BaseModel):
    user: str

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title= "Fast"
)

@app.get("/get_user")
def get_user(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/get_user/{id}")
def get_user(id:int,db: Session = Depends(get_db)):
    users = db.query(User).filter_by(id=id).first()
    return users



@app.post("/create_users")
def create_user(user: UserModel, db: Session = Depends(get_db)):
    new_user = User(user=user.user)
    db.add(new_user)
    try:
        db.commit()
        return new_user
    except SQLAlchemyError:
        db.rollback()
        return {"error": "Failed to create user"}
    
@app.put("/update_user/{id}")
def update_user(id:int,user:UserModel, db:Session = Depends(get_db)):
    user_record = db.query(User).filter_by(id = id).first()
    user_record.user = user.user
    try:
        db.commit()
        return user_record
    except SQLAlchemyError:
        db.rollback()
        return {"error": "Failed to update user"}
    
@app.delete("/delete_user/{id}")
def delete_user(id:int,user:UserModel, db:Session = Depends(get_db)):
    user_record = db.query(User).filter_by(id=id).first()
    try:
        db.delete(user_record)
        db.commit()
        return user_record
    except SQLAlchemyError:
        db.rollback()
        return {"error": "Failed to delete user"}

@app.get("/find_factorial/{n}")
def find_factorial(n: int):
    url = "https://jvikx3uk4i.execute-api.us-east-1.amazonaws.com/default/factorial"
    response = requests.post(url, json={"number": n})
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to calculate factorial"}