from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from auth import require_admin
from services import resume_service
from models import User, ResumeAnalysis
from auth import get_current_user
from fastapi.responses import FileResponse # tells FastAPI to return a file's contents as an HTTP response.
from fastapi import HTTPException
from schema import ResumeAnalysisResponse
from services.resume_analyzer import analyze_resume as analyze_resume_text, OLLAMA_MODEL # to record which model generated each analysis
import hashlib # SHA-256 is a cryptographic hash function. It takes text as input and produces a fixed-length fingerprint.
# The same text produces the same hash.
# Different text will overwhelmingly likely produce a different hash.

from database import get_db
from schema import (
    MessageResponse,
    ResumeDetailResponse,
    ResumeResponse,
    ResumeCreateResponse,
    ResumeUpdateResponse,
    ResumeTextResponse,
    SavedResumeAnalysisResponse
)

router = APIRouter(prefix="/resumes", tags=["Resumes"])

# -------------------------
# CREATE RESUME
# -------------------------

# A user can create one or more than one resume for themselves

@router.post("/", response_model=ResumeCreateResponse)
def create_resume(
                  # Get title from the form data sent in the request.
                  # ... Means this field is required
                  title: str = Form(...),
                  file: UploadFile = File(...),
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
        return resume_service.create_resume(db, title, file, current_user)

# -------------------------
# CREATE RESUME
# -------------------------

# Admins can create resumes for a specific user using user_id
# The name of user_id in the URL and user_id parameter that the create_user_resume function receives must be the same
# Once the names are the same the value from the URL is passed to the function 

@router.post("/{user_id}/resumes", response_model=ResumeCreateResponse)
def create_user_resume(
    user_id: int,
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return resume_service.create_user_resume(
        db,
        user_id,
        title,
        file
    )

# -------------------------
# GET ALL RESUMES
# -------------------------

# A user gets all resumes that they have created

@router.get("/", response_model=list[ResumeResponse])
def get_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return resume_service.get_resumes(db, current_user)

# -------------------------
# GET RESUME BY ID
# -------------------------

# A user gets a specific resume by ID

@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(resume_id: int, 
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):

       return resume_service.get_resume(db, resume_id, current_user)

# -------------------------
# UPDATE RESUME
# -------------------------

@router.put("/{resume_id}", response_model=ResumeUpdateResponse)
def update_resume(
    resume_id: int,
    title: str | None = Form(default=None), #title is optional. The user can leave it out if they only want to replace the file.
    file: UploadFile | None = File(default=None), # file is optional. The user can leave it out if they only want to change the title.
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    # Before running update_resume(), use get_current_user() to find out who is making this request.

):
    return resume_service.update_resume(
        db,
        resume_id,
        title,
        file,
        current_user
    )

# -------------------------
# DELETE RESUME
# -------------------------

@router.delete("/{resume_id}", response_model=MessageResponse)
def delete_resume(resume_id: int, 
                  db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_user)):
        return resume_service.delete_resume(db, resume_id, current_user)


# -------------------------
# DOWNLOAD A RESUME
# -------------------------

@router.get(
    "/{resume_id}/download",
    response_class=FileResponse
)
def download_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_path = resume_service.get_resume_for_download(
        db,
        resume_id,
        current_user
    )

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
        headers={
        "Cache-Control": "no-store, private",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    )

# -------------------------
# EXTRACT RESUME TEXT
# -------------------------

@router.get(
    "/{resume_id}/text",
    response_model=ResumeTextResponse
)
def read_resume_text(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return resume_service.get_resume_text(
        db,
        resume_id,
        current_user
    )

# -------------------------
# ANALYZE RESUME TEXT
# -------------------------


@router.post(
    "/{resume_id}/analyze",
    response_model=ResumeAnalysisResponse
)
def analyze_resume_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Retrieve the resume text and verify access permissions.
    resume_data = resume_service.get_resume_text(
        db,
        resume_id,
        current_user
    )

    resume_text = resume_data["extracted_text"]

    # 2. Analyze the resume using Ollama.
    try:
        analysis = analyze_resume_text(
            resume_data["extracted_text"]
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc

    # 3. Calculate the SHA-256 hash of the resume text.
    content_hash = hashlib.sha256(
        resume_text.encode("utf-8")
    ).hexdigest()


    # 4. Create a database record for this analysis.
    new_analysis = ResumeAnalysis(
        resume_id=resume_data["resume_id"],
        analysis_result=analysis,
        model_name=OLLAMA_MODEL,
        resume_text_snapshot=resume_text,
        content_hash=content_hash
    )
    # We don't provide id because PostgreSQL generates it automatically.
    # We don't provide created_at because we configured server_default=func.now() in our model.


    # 5. Save the analysis in PostgreSQL.
    try:
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)

    except SQLAlchemyError as exc: # database-related errors raised by SQLAlchemy.
        db.rollback() # cancels the failed transaction and resets the session so it can be used agains
        raise HTTPException(
            status_code=500,
            detail="Could not save the resume analysis."
        ) from exc

    # 6. Return the analysis to the frontend.
    return {
        "resume_id": resume_data["resume_id"],
        "title": resume_data["title"],
        **analysis # unpacks the six key-value pairs from the analysis dictionary into the new dictionary
    }

# -------------------------
# RETRIVE THE LATEST AI ANALYSIS IN THE DATABASE
# ------------------------

@router.get(
    "/{resume_id}/analysis",
    response_model=SavedResumeAnalysisResponse
)
def read_latest_resume_analysis(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return resume_service.get_latest_resume_analysis(
        db,
        resume_id,
        current_user
    )
