from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.lib.db import get_db
from app.models.model import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    SignupResponse,
    LogoutResponse,
)
from app.api.auth.functions import (
    signup_handler,
    login_handler,
    relogin_handler,
    logout_handler,
)


auth_route = APIRouter(tags=["Auth"], prefix="/auth")


@auth_route.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    try:
        res = signup_handler(request, db)
        return JSONResponse(
            status_code=200,
            content=res.model_dump(),
        )
    except Exception as e:
        raise e


@auth_route.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        access_token, refresh_token = login_handler(request, db)
        return JSONResponse(
            status_code=200,
            content={"access_token": access_token, "refresh_token": refresh_token},
        )
    except Exception as e:
        raise e


@auth_route.post("/relogin", response_model=TokenResponse)
def relogin(refresh_token: str = Header(...), db: Session = Depends(get_db)):
    try:
        new_access_token, new_refresh_token = relogin_handler(refresh_token, db)
        return JSONResponse(
            status_code=200,
            content={
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            },
        )
    except Exception as e:
        raise e


@auth_route.post("/logout", response_model=LogoutResponse)
def logout(refresh_token: str = Header(...), db: Session = Depends(get_db)):
    try:
        deleted, username = logout_handler(refresh_token, db)
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Logged out successfully. {deleted} session(s) removed.",
                "username": username,
            },
        )
    except Exception as e:
        raise e

