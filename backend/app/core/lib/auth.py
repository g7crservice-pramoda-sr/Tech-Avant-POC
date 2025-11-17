import jwt
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.lib import auth
from app.core.lib.db import get_db
from app.models.model import SerializedUser as SerializedUser
from app.models.sql_model import UserSessions, Users

SECRET_KEY = "opensource4lyf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 3
REFRESH_TOKEN_EXPIRE_DAYS = 1

security = HTTPBearer()  # Authorization: Bearer <token>


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> SerializedUser:
    """
    Get current user from token.
    Args:
        token (HTTPAuthorizationCredentials): The token. <fastapi.security.HTTPAuthorizationCredentials>
        db (Session): The database session. <sqlalchemy.orm.Session>

    Returns:
        user: The user object. <app.models.model.Users>
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    unknown_user = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unknown user",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = auth.decode_token(token.credentials)
        if payload.get("type") != "access":
            raise credentials_exception
        username = payload.get("sub")

        # DB session check (access token must exist in DB)
        user = db.query(Users).filter_by(username=username).first()
        if not user:
            raise unknown_user
        session = (
            db.query(UserSessions)
            .filter_by(userId=user.id, accessToken=token.credentials)
            .first()
        )

        if not session:
            raise credentials_exception

        return SerializedUser(
            id=str(user.id),
            username=user.username,
            role=user.role,
            createdAt=user.createdAt.isoformat(),
            updatedAt=user.updatedAt.isoformat(),
        )

    except Exception:
        raise credentials_exception


def create_access_token(data: dict) -> str:
    """
    Create access token.
    Args:
        data (dict): The data.

    Returns:
        str: The access token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create refresh token.
    Args:
        data (dict): The data.

    Returns:
        str: The refresh token
    """
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise e


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode token.
    Args:
        token (str): The token.

    Returns:
        dict: The decoded token
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
