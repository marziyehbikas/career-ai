from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schema import (
    MessageResponse,
    UserCreate,
    UserCreateResponse,
    UserUpdate,
    UserListResponse,
    UserDetailResponse,
    UserUpdateResponse,
)
from services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

# -------------------------
# CREATE USER
# -------------------------

@router.post("/users", response_model = UserCreateResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
     return user_service.create_user(db, user)

# -------------------------
# GET ALL USERS
# -------------------------

@router.get("/users", response_model=UserListResponse)
def get_users(name: str | None = None, 
              email: str | None = None,
              sort: str | None = None,
              page: int = Query(default=1, ge=1), # Quesry check that the URL parameters are valid. #default value = 1, minimum value = 1
              limit: int = Query(default=10, ge=1, le=100), # Maximum number of rows # default value = 10, minimum value = 1, maximum value = 100
              db: Session = Depends(get_db)):  

        return user_service.get_users(db, name, email, sort, page, limit)


# -------------------------
# GET USER BY ID
# -------------------------

@router.get("/users/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
        return user_service.get_user(db, user_id)


# -------------------------
# UPDATE USER
# -------------------------

@router.put("/users/{user_id}", response_model=UserUpdateResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
      return user_service.update_user(db, user_id, user)

# -------------------------
# DELETE USER
# -------------------------

@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
        return user_service.delete_user(db, user_id)
