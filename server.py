from fastapi import FastAPI, Depends, HTTPException
from pymongo import MongoClient
from passlib.context import CryptContext
from bson.objectid import ObjectId
from pydantic import BaseModel

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["WIN_project"]
    return db

class UserCreate(BaseModel):
    username: str
    password: str

app = FastAPI()

db = get_db()
users_collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/register")
def register(user: UserCreate):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = {"username": user.username, "password": hashed_password}
    
    result = users_collection.insert_one(new_user)
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

@app.post("/login")
def login(user: UserCreate):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    return {"message": "Login successful", "user_id": str(db_user["_id"])}
