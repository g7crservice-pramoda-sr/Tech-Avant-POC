import os
from dotenv import load_dotenv
from typing import Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from passlib.context import CryptContext

from app.core.lib.auth import create_access_token, create_refresh_token, decode_token
from app.models.model import (
    SignupRequest,
    LoginRequest,
    SignupResponse,
    SerializedUser as SerializedUser,
)
from app.models.sql_model import Users, UserSessions


load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin@123")

# Azure OpenAI Credentials
AZURE_OPENAI_RESOURCE_NAME = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------------------------------------------------------------
# Fuction Handlers
# ----------------------------------------------------------------------------
def signup_handler(request: SignupRequest, db: Session) -> SignupResponse:
    """
    Handles the signup process for a new user.
    Args:
        request (SignupRequest): The signup request data. <app.models.model.SignupRequest>
        db (Session): The database session. <sqlalchemy.orm.Session>

    Returns:
        SignupResponse: A SignupResponse object. <app.models.model.SignupResponse>
    """
    try:
        if request.admin_password != ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid admin password")

        existing_user = (
            db.query(Users).filter(Users.username == request.username).first()
        )
        if existing_user:
            raise HTTPException(status_code=409, detail="Username already exists")

        hashed_pw = pwd_context.hash(request.password)
        new_user = Users(
            username=request.username, password=hashed_pw, role=request.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return SignupResponse(
            success=True,
            user=SerializedUser(
                id=str(new_user.id),
                username=new_user.username,
                role=new_user.role,
                createdAt=new_user.createdAt.isoformat(),
                updatedAt=new_user.updatedAt.isoformat(),
            ),
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail="An error occurred during signup: " + str(e)
        )


def login_handler(request: LoginRequest, db: Session) -> Tuple[str, str]:
    """
    Handles the login process for an existing user.
    Args:
        request (LoginRequest): The login request data. <app.models.model.LoginRequest>
        db (Session): The database session. <sqlalchemy.orm.Session>

    Returns:
        (access_token, refresh_token): A Tuple containing the access token and refresh token.
    """
    try:
        user = db.query(Users).filter(Users.username == request.username).first()
        if not user or not pwd_context.verify(request.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        access_token = create_access_token({"sub": user.username})
        refresh_token = create_refresh_token({"sub": user.username})

        # Clean up: delete all existing session
        db.query(UserSessions).filter(UserSessions.userId == user.id).delete()

        # Save session
        db_session = UserSessions(
            userId=user.id,
            accessToken=access_token,
            refreshToken=refresh_token,
        )
        db.add(db_session)
        db.commit()
        return access_token, refresh_token

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail="An error occurred during login: " + str(e)
        )


def relogin_handler(refresh_token: str, db: Session):
    """
    Handles the relogin process for an existing user.
    Args:
        refresh_token (str): The refresh token.
        db (Session): The database session. <sqlalchemy.orm.Session>

    Returns:
        (access_token, refresh_token): A Tuple containing the new access token and refresh token.
    """
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token. "
            )

        username = payload.get("sub")
        session = db.query(UserSessions).filter_by(refreshToken=refresh_token).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        new_access_token = create_access_token({"sub": username})
        new_refresh_token = create_refresh_token({"sub": username})

        # Update session
        session.accessToken = new_access_token
        session.refreshToken = new_refresh_token
        session.updatedAt = datetime.now(timezone.utc)
        db.commit()

        return new_access_token, new_refresh_token
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail="An error occurred during relogin: " + str(e)
        )


def logout_handler(refresh_token: str, db: Session):
    """
    Handles the logout process for an existing user.
    Args:
        refresh_token (str): The refresh token.
        db (Session): The database session. <sqlalchemy.orm.Session>

    Returns:
        (deleted, username): A Tuple containing the number of deleted sessions and the username.
    """
    try:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        username = payload.get("sub")

        user = db.query(Users).filter_by(username=username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        deleted = db.query(UserSessions).filter_by(userId=user.id).delete()
        db.commit()

        return deleted, username
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        elif isinstance(e, ValueError):
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        raise HTTPException(
            status_code=500, detail="An error occurred during logout: " + str(e)
        )
