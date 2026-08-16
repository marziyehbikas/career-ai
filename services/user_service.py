from fastapi import HTTPException, Query
from models import User
from schema import UserCreate, UserUpdate
from sqlalchemy.orm import joinedload
import math
from sqlalchemy.orm import Session


# -------------------------
# CREATE USER
# -------------------------

def create_user(db: Session, user: UserCreate):
        new_user = User(
            name=user.name,
            email=user.email
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email
            }
        }


# -------------------------
# GET ALL USERS
# -------------------------

def get_users(db: Session, name = None, email = None, sort = None, page = 1, limit = 10): 
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
# UPDATE USER
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
            "user": {
                "id": existing_user.id,
                "name": existing_user.name,
                "email": existing_user.email
            }
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