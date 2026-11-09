import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

from sqlalchemy.orm import Session

from database import get_db
from models import User
from config import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()

# Token creation function
def create_access_token(user_id: int, expires_minutes: int = 30):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# Get the current user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), # Before running get_current_user(), use bearer_scheme to get the token from the request.
    db: Session = Depends(get_db)
):

    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user

# Check if the logged-in user is an admin
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user