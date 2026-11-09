from fastapi import HTTPException
from models import User
from schema import UserCreate, UserUpdate, UserLogin
from sqlalchemy.orm import joinedload
import math
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from auth import create_access_token

# -------------------------
# HASH THE PASSWORD
# -------------------------

password_hash = PasswordHash.recommended()
# password_hash is an object that knows how to hash and verify passwords. 
# We use it to hash passwords.

# -------------------------
# VERIFY THE PASSWORD
# -------------------------

# Verify if the password that the user entered is the same is the password stored in the DB

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
                                # the password the user just entered
                                                # the hash stored in PostgreSQL
# -------------------------
# LOGIN
# -------------------------

def login_user(db: Session, user: UserLogin):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(existing_user.id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": existing_user
    } 

# -------- USER --------- # 

# -------------------------
# UPDTAE PROFILE
# -------------------------

def update_profile(db, user, current_user):
    # Emails are unique in the DB so if a user updates their profile and enters an email that is already in the DB for another user they will get an error
    existing_user = db.query(User).filter(
         User.email == user.email,
         User.id != current_user.id
        ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already in use"
        )

    current_user.name = user.name
    current_user.email = user.email

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated!",
        "user": current_user
    }

# -------------------------
# DELETE PROFILE
# -------------------------
def delete_profile(
    db: Session,
    current_user
):
    db.delete(current_user)
    db.commit()

    return {
        "message": "Account deleted"
    }

# -------------------------
# CREATE USER
# -------------------------

def create_user(db: Session, user: UserCreate):
        hashed_password = password_hash.hash(user.password)

        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created",
            "user": new_user
        }

# -------------------------
# CHANGE PASSWORD
# -------------------------

def update_password(db, password_data, current_user):

    if not verify_password(
        password_data.current_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect"
        )

    current_user.password_hash = password_hash.hash(
        password_data.new_password
    )

    db.commit()

    return {
        "message": "Password updated successfully"
    }
          

# -------- ADMIN -------- # 

# -------------------------
# GET ALL USERS
# -------------------------

def get_users(db: Session, 
              name = None, 
              email = None, 
              sort = None, 
              page = 1, 
              limit = 10): 
        
        query = db.query(User)

        if name:
            query = query.filter(User.name == name)

        if email:
            query = query.filter(User.email == email)

        if sort == "name":
            query = query.order_by(User.name)

        if sort == "name_desc":
            query = query.order_by(User.name.desc())

        if sort == "email":
            query = query.order_by(User.email)

        offset = (page - 1) * limit # The number of rows that should be skipped 
        total_users = query.count() # The total number of users 
        total_pages = math.ceil(total_users / limit) # The total number of pages. For decimal numbers, ceil rounds them up 
        # For example, 100 total users / 10 limit = 10 pages > we are going to have 10 pages which show 10 users each

        users = (
                    query
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

        return {
            "page": page,
            "limit": limit,
            "total_users": total_users,
            "total_pages": total_pages,
            "data": users
        }


# -------------------------
# GET USER BY ID
# -------------------------

def get_user(db: Session, user_id: int):
        user = (
            db.query(User)
            .options(joinedload(User.resumes))
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user


# -------------------------
# UPDATE USER BY ADMIN
# -------------------------

def update_user(db: Session, user_id: int, user: UserUpdate):
        existing_user = db.query(User).filter(User.id == user_id).first()

        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        existing_user.name = user.name
        existing_user.email = user.email

        db.commit()
        db.refresh(existing_user)

        return {
            "message": "User updated",
            "user": existing_user
        }

# -------------------------
# DELETE USER
# -------------------------

def delete_user(db: Session, user_id: int):
        existing_user = db.query(User).filter(User.id == user_id).first()

        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        db.delete(existing_user)
        db.commit()

        return {
            "message": "User deleted"
        }

# -------------------------
# CHANGE USER'S ROLE
# -------------------------

def update_user_role(db: Session, user_id: int, role: str, admin_user):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == admin_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot change your own role"
    )

    # The user is currently an admin AND we want to change them to a normal user
    if user.role == "admin" and role == "user":
        admin_count = db.query(User).filter(
            User.role == "admin"
        ).count()

        if admin_count == 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last admin"
            )

    user.role = role

    db.commit()
    db.refresh(user)

    return {
        "message": "User's role updated",
        "user": user
    }