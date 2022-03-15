from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # Bcrypt can't parse passwords longer than 72 characters.