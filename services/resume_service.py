from fastapi import HTTPException
from schema import ResumeCreate, ResumeUpdate, ResumeListResponse
from sqlalchemy.orm import Session
from models import User, Resume

# -------------------------
# CREATE RESUME
# -------------------------

def create_resume(db: Session, resume: ResumeCreate):
        user = db.query(User).filter(
            User.id == resume.user_id).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        new_resume = Resume(
            title=resume.title,
            file_path=resume.file_path,
            user_id=resume.user_id
        )

        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)

        return new_resume

# -------------------------
# GET ALL RESUMES
# -------------------------

def get_resumes(db: Session):
        resumes = db.query(Resume).all()

        return resumes

# -------------------------
# GET RESUME BY ID
# -------------------------

def get_resume(db: Session, resume_id: int):

        resume = db.query(Resume).filter(Resume.id == resume_id).first()

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        return resume




# -------------------------
# UPDATE RESUME
# -------------------------

def update_resume(db: Session, resume_id: int, resume: ResumeUpdate):

        existing_resume = db.query(Resume).filter(
            Resume.id == resume_id
        ).first()

        if not existing_resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )
        
        existing_user = db.query(User).filter(User.id == resume.user_id).first()

        if not existing_user:
            raise HTTPException(
                status_code = 404,
                detail = "User Not Found"
            )
        
        existing_resume.title = resume.title
        existing_resume.file_path = resume.file_path
        existing_resume.user_id = resume.user_id

        db.commit()
        db.refresh(existing_resume)

        return {
            "message": "Resume updated",
            "resume": {
                "id": existing_resume.id,
                "title": existing_resume.title,
                "file_path": existing_resume.file_path,
                "user_id": existing_resume.user_id
            }
        }

# -------------------------
# DELETE RESUME
# -------------------------

def delete_resume(db: Session, resume_id: int):
        existing_resume = db.query(Resume).filter(
            Resume.id == resume_id
        ).first()

        if not existing_resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        db.delete(existing_resume)
        db.commit()

        return {
            "message": "Resume deleted"
        }
