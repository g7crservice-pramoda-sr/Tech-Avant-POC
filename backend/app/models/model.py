from pydantic import BaseModel
from typing import Literal

# ------------------------------------------------------------------------------
# Database Schema Models
# ------------------------------------------------------------------------------
class SerializedUser(BaseModel):
    id: str
    username: str
    role: str
    createdAt: str
    updatedAt: str

# ------------------------------------------------------------------------------
# Request pydantic models
# ------------------------------------------------------------------------------
class SignupRequest(BaseModel):
    admin_password: str
    username: str
    password: str
    role: Literal["admin", "user"]


class LoginRequest(BaseModel):
    username: str
    password: str



# ------------------------------------------------------------------------------
# Response pydantic models
# ------------------------------------------------------------------------------

class SignupResponse(BaseModel):
    success: Literal[True]
    user: SerializedUser


class LogoutResponse(BaseModel):
    message: str
    username: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str