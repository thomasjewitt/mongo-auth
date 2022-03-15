from fastapi import FastAPI, Cookie
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from os import getenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError
from api.db import DBManager
from api.models import User

app = FastAPI()
db_manager = DBManager()

SECRET_KEY = getenv("SECRET_KEY")
ctx = CryptContext(schemes=["bcrypt"])


@app.post("/register/")
def create_user(user: User):
    try:
        user_data = user.__dict__
        hash = ctx.hash(user_data.pop("password"))
        user_data["hash"] = hash
        result = db_manager.add_user_to_db(user_data)
        result.pop("_id")
        result.pop("hash")
        return JSONResponse(status_code=201, content=result)
    except DuplicateKeyError:
        return JSONResponse(status_code=409, content={"error": "A user with that email already exists."})


@app.post("/login/")
def login_user(user: User):
    db_user = db_manager.retrieve_user_by_email(user.email)
    if not db_user:
        return JSONResponse(status_code=404, content={"error": "User not found."})
    result = ctx.verify(user.password, db_user["hash"])
    if result:
        expiry = datetime.now() + timedelta(minutes=60)
        dict_to_encode = {
            "email": user.email,
            "exp": expiry
        }
        try:
            token = jwt.encode(dict_to_encode, SECRET_KEY, algorithm="HS256")
            response = JSONResponse(status_code=200, content={"token": token})
            response.set_cookie(key="token", value=token, secure=True, httponly=True)
            return response
        except JWTError:
            return JSONResponse(status_code=500, content={"error": "Error generating JWT."})
    else:
        return JSONResponse(status_code=401, content={"error": "Incorrect password."})


@app.get("/userinfo/")
def get_user_info(token: str | None = Cookie(None)):
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not logged in."})
    else:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return JSONResponse(status_code=200, content={"email": decoded_token["email"]})
        except JWTError:
            return JSONResponse(status_code=401, content={"error": "Invalid token."})