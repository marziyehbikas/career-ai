from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schema import (
    MessageResponse,
    ResumeCreate,
    ResumeDetailResponse,
    ResumeListResponse,
    ResumeUpdate,
)
from services import resume_service

router = APIRouter(prefix="/resumes", tags=["Resumes"])

# -------------------------
# CREATE RESUME
# -------------------------

@router.post("/resumes", response_model=ResumeListResponse)
def create_resume(resume: ResumeCreate, db: Session = Depends(get_db)):
        return resume_service.create_resume(db, resume)

# -------------------------
# GET ALL RESUMES
# -------------------------

@router.get("/resumes", response_model=ResumeListResponse)
def get_resumes(db: Session = Depends(get_db)):
        return resume_service.get_resumes(db)

# -------------------------
# GET RESUME BY ID
# -------------------------

@router.get("/resumes/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):

       return resume_service.get_resume(db, resume_id)

# -------------------------
# UPDATE RESUME
# -------------------------

@router.put("/resumes/{resume_id}", response_model=ResumeDetailResponse)
def update_resume(resume_id: int, resume: ResumeUpdate, db: Session = Depends(get_db)):

        return resume_service.update_resume(db, resume_id, resume)

# -------------------------
# DELETE RESUME
# -------------------------

@router.delete("/resumes/{resume_id}", response_model=MessageResponse)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
        return resume_service.delete_resume(db, resume_id)

