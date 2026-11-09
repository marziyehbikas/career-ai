from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services import user_service
from auth import require_admin
from models import User
from schema import RoleUpdate
from auth import get_current_user
from schema import (
    MessageResponse,
    UserCreate,
    UserCreateResponse,
    UserUpdate,
    UserPaginationResponse,
    UserResponse,
    UserDetailResponse,
    UserUpdateResponse,
    UserLogin, 
    LoginResponse,
    AdminUserResponse,
    PasswordUpdate
)

router = APIRouter(prefix="/users", tags=["Users"])

# -------- USER --------- # 

# -------------------------
# CREATE USER
# -------------------------

@router.post("/", response_model = UserCreateResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
     return user_service.create_user(db, user)


# -------------------------
# LOGIN
# -------------------------

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return user_service.login_user(db, user)

# -------------------------
# USER'S PROFILE
# -------------------------

@router.get("/profile", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

# -------------------------
# UPDATE PROFILE
# -------------------------

@router.put("/profile", response_model=UserUpdateResponse)
def update_profile(user: UserUpdate,
                   db: Session = Depends(get_db), 
                   current_user: User = Depends(get_current_user)):

      return user_service.update_profile(db, user, current_user)

# -------------------------
# DELETE PROFILE
# -------------------------

@router.delete("/profile", response_model=MessageResponse)
def delete_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

      return user_service.delete_profile(db, current_user)

# -------------------------
# CHANGE PASSWORD
# -------------------------

@router.put("profile/password", response_model=MessageResponse)
def update_password(password_data: PasswordUpdate, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):

      return user_service.update_password(db, password_data, current_user)

# -------- ADMIN -------- # 

# -------------------------
# GET ALL USERS
# -------------------------

@router.get("/", response_model=UserPaginationResponse)
def get_users(name: str | None = None, 
              email: str | None = None,
              sort: str | None = None,
              page: int = Query(default=1, ge=1), # Query check that the URL parameters are valid. #default value = 1, minimum value = 1
              limit: int = Query(default=10, ge=1, le=100), # Maximum number of rows # default value = 10, minimum value = 1, maximum value = 100
              db: Session = Depends(get_db),
              admin_user: User = Depends(require_admin)): # Check if the logged-in user is an admin before you run this function, if they are an admin they can see the list of the users

        return user_service.get_users(db, name=name, email=email, sort=sort, page=page, limit=limit)

# -------------------------
# GET USER BY ID
# -------------------------

@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: int, 
             db: Session = Depends(get_db),  
             admin_user: User = Depends(require_admin)):
        return user_service.get_user(db, user_id)

# -------------------------
# UPDATE USER
# -------------------------

@router.put("/{user_id}", response_model=UserUpdateResponse)
def update_user(user_id: int, 
                user: UserUpdate, 
                db: Session = Depends(get_db),
                admin_user: User = Depends(require_admin)):
      return user_service.update_user(db, user_id, user)

# -------------------------
# CHANGE USER'S ROLE
# -------------------------

@router.patch("/{user_id}/role", response_model=AdminUserResponse)
def update_user_role(
    user_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return user_service.update_user_role(
        db,
        user_id,
        role_data.role,
        admin_user
    )

# -------------------------
# DELETE USER
# -------------------------

@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, 
                db: Session = Depends(get_db), 
                admin_user: User = Depends(require_admin)):
        
        return user_service.delete_user(db, user_id)