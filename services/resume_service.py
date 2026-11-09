from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from models import User, Resume, ResumeAnalysis
from sqlalchemy.orm import joinedload
from pathlib import Path
from uuid import uuid4
import shutil
import logging
from services.resume_text_extractor import extract_resume_text

# -------------------------
# CREATE RESUME
# -------------------------

# A user creates resumes for themselves

UPLOAD_DIR = Path("uploads/resumes")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
                                      
def create_resume(
        # Indicates the type of the variable
    db: Session, 
    title: str,
    file: UploadFile,
    current_user
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing"
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )

    # Creates folders in our path (uploads/resumes)
    UPLOAD_DIR.mkdir(
        parents=True, # Create the parent directories (upload folder) too, if they don't already exist
        exist_ok=True # If the directory already exists, do nothing
    )

    # Creates a new unique filename to save in the DB to avoid duplication
    filename = f"{uuid4()}{extension}"
    # Creates the complete location
    file_path = UPLOAD_DIR / filename

    # Take the uploaded file and copy it into our uploads/resumes folder
    # wb means to write as brinary
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_resume = Resume(
        title=title,
        file_path=str(file_path),
        user_id=current_user.id
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "message": "Resume created!",
        "resume": new_resume
    }

# -------------------------
# CREATE RESUME
# -------------------------

# Admins can create resumes for a user

def create_user_resume(
    db: Session,
    user_id: int,
    title: str,
    file: UploadFile
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is missing"
            )
    
    extension = Path(file.filename).suffix.lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Creates folders in our path (uploads/resumes)
    UPLOAD_DIR.mkdir(
        parents=True, # Create the parent directories (upload folder) too, if they don't already exist
        exist_ok=True # If the directory already exists, do nothing
    )
    
    # Creates a new unique filename to save in the DB to avoid duplication
    filename = f"{uuid4()}{extension}"
    # Creates the complete location
    file_path = UPLOAD_DIR / filename
    
    # Take the uploaded file and copy it into our uploads/resumes folder
    # wb means to write as brinary
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    new_resume = Resume(
        title=title,
        file_path=str(file_path),
        user_id=user.id
    )
    
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    return {
        "message": "Resume created!",
        "resume": new_resume
    }

# -------------------------
# DOWNLOAD RESUME
# -------------------------

# Users can download their resumes 

def get_resume_for_download(
    db: Session,
    resume_id: int,
    current_user
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # Only the owner or an admin can access the resume.
    if (
        current_user.role != "admin"
        and resume.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to download this resume"
        )

    # Path(a path) turns the path into a Path object that you can work with
    # Relative path: uploads/resumes/26a43edf-b702-45db-bb0b-5940dcb567fd.pdf
    file_path = Path(resume.file_path)

    # Ensure that the file is inside our private upload directory.
    upload_root = Path("uploads/resumes").resolve()
    resolved_path = file_path.resolve()
    # resolve() converts the path into an absolute path
    # absolute path: D:\Projects\career-ai-backend\uploads\resumes\26a43edf-b702-45db-bb0b-5940dcb567fd.pdf

    # Is this path inside the directory represented by upload_root, or is it that directory itself?
    if not resolved_path.is_relative_to(upload_root):
        raise HTTPException(
            status_code=403,
            detail="Invalid resume file path"
        )

    # Checks whether a file exists at that location.
    if not resolved_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found on server"
        )

    return resolved_path

# -------------------------
# GET ALL RESUMES
# -------------------------

def get_resumes(db: Session, current_user):
    if current_user.role == "admin":
        resumes = db.query(Resume).all()
    else:
        resumes = db.query(Resume).filter(
            Resume.user_id == current_user.id
        ).all()

    return resumes

# -------------------------
# GET RESUME BY ID
# -------------------------

def get_resume(db: Session, resume_id: int, current_user):

    resume = (
        db.query(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.id == resume_id)
        .first()
        )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    if current_user.role != "admin" and resume.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this resume"
        )

    return resume

# -------------------------
# UPDATE RESUME
# -------------------------

def update_resume(
    db: Session,
    resume_id: int,
    title: str | None,
    file: UploadFile | None,
    current_user
):
    # 1. Find the resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # 2. Check permissions
    if (
        current_user.role != "admin"
        and resume.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this resume"
        )

    # 3. Require at least one change
    if title is not None:
        title = title.strip() # Strip removes extra spaces from both sides of the string

    if title == "": # If users enter a space 
        title = None

    if title is None and file is None:
        raise HTTPException(
            status_code=400,
            detail="Provide a title or a replacement file"
        )

    # Remember the current file path
    old_file_path = (
        Path(resume.file_path)
        if resume.file_path
        else None
    )

    new_file_path = None

    # 4. Save a replacement file, if provided
    if file is not None:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is missing"
            )

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are allowed"
            )

        # Calling this again doesn't delete or recreate an existing directory or its contents. 
        # It simply makes sure the required directory exists.
        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        new_file_path = UPLOAD_DIR / f"{uuid4()}{extension}"

        try:
            with new_file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except OSError as exc:
            # If saving fails, remove the incomplete new file
            if new_file_path.is_file():
                new_file_path.unlink()

            raise HTTPException(
                status_code=500,
                detail="Could not save the uploaded file"
            ) from exc
              # "from exc" means "this new exception was caused by the exception stored in exc

    # 5. Update the database record
    if title is not None:
        resume.title = title

    if new_file_path is not None:
        resume.file_path = str(new_file_path)

    # Save database changes
    try:
        db.commit()

    except Exception:
        # Resets the current transaction and resets the session after a failure.
        db.rollback()

        # Remove the new file if the database update fails
        if new_file_path is not None and new_file_path.is_file():
            try:
                new_file_path.unlink()
            except OSError:
                pass

        raise

    db.refresh(resume)

    # 6. Delete the old file, but only after the database
    # update succeeds, and only if it is inside our upload folder
    if new_file_path is not None and old_file_path is not None:
        try:
            upload_root = UPLOAD_DIR.resolve()
            old_path = old_file_path.resolve()

            if (
                old_path.is_relative_to(upload_root)
                and old_path.is_file()
            ):
                old_path.unlink()

        except OSError:
            # The update has succeeded, but cleanup may have failed.
            # The old file might remain on disk.
            pass

    return {
        "message": "Resume updated!",
        "resume": resume
    }

# -------------------------
# DELETE RESUME
# -------------------------

# a built-in Python module that lets your application record messages about what's happening while it runs.
logger = logging.getLogger(__name__)


def delete_resume(
    db: Session,
    resume_id: int,
    current_user
):
    # 1. Find the resume in the database
    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # 2. Check permissions before deleting anything
    if (
        current_user.role != "admin"
        and resume.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this resume"
        )

    # 3. Remember the file path before deleting the record
    stored_file_path = (
        Path(resume.file_path)
        if resume.file_path # whether the database record has a truthy file_path value
        else None
    ) # Creates a Path object if a path value exists; otherwise returns None.

    # 4. Delete the database record first
    db.delete(resume)

    try:
        db.commit()
    except Exception:
        db.rollback() # Reset the database session
        raise # Re-raises and returns the error and finishes the function here

    # 5. Delete the physical file after the database commit
    if stored_file_path is not None:
        try:
            upload_root = UPLOAD_DIR.resolve()
            resolved_path = stored_file_path.resolve()

            # Never delete a file outside our resume directory
            if not resolved_path.is_relative_to(upload_root):
                logger.warning(
                    # The %s tells the logging system where to insert the value of resolved_path
                    "Skipped deleting file outside upload directory: %s",
                    resolved_path
                )

            elif resolved_path.is_file():
                resolved_path.unlink() # Deletes the file

        except OSError:
            logger.exception(
                "Resume record %s was deleted, but file cleanup failed",
                resume_id
            )

    return {
        "message": "Resume deleted successfully"
    }

# -------------------------
# EXTRACT RESUME TEXT
# -------------------------

def get_resume_text(
    db: Session,
    resume_id: int,
    current_user: User
):
    # 1. Find the resume in the database.
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id)
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    # 2. Check whether the user has permission to access it.
    if (
        current_user.role != "admin"
        and resume.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resume."
        )

    # 3. Check that the resume has a stored file path.
    if not resume.file_path:
        raise HTTPException(
            status_code=404,
            detail="Resume file path not found."
        )

    file_path = Path(resume.file_path).resolve()
    upload_root = UPLOAD_DIR.resolve()

    # 4. Make sure the file is inside our resume upload directory.
    if not file_path.is_relative_to(upload_root):
        raise HTTPException(
            status_code=400,
            detail="Invalid resume file path."
        )

    # 5. Check that the file actually exists.
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found on the server."
        )

    # 6. Extract the text using our existing function.
    try:
        extracted_text = extract_resume_text(file_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc
    # If extraction fails, raise a ValueError and call it exc (ValueError is a Python Error)
    # The valueError can only catch value errors such as unsupported extensions 
    # Then we raise and HTTPException error (API Error so our API can return it to the client)
    # We link this HTTP error to our original ValueError using from exc

    # 7. Handle files from which no text could be extracted.
    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No readable text could be extracted from this resume. "
                "The file may be scanned or image-based."
            )
        )

    # 8. Return the information required by our response schema.
    return {
        "resume_id": resume.id,
        "title": resume.title or "Untitled resume",
        "extracted_text": extracted_text,
        "character_count": len(extracted_text)
    }

# -------------------------
# RETRIVE THE LATEST AI ANALYSIS IN THE DATABASE
# ------------------------

def get_latest_resume_analysis(
    db: Session,
    resume_id: int,
    current_user: User
):
    # 1. Find the resume.
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id)
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    # 2. Check whether the current user can access the resume.
    if current_user.role != "admin" and resume.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resume."
        )

    # 3. Find the most recent saved analysis.
    latest_analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume_id)
        .order_by(
            ResumeAnalysis.created_at.desc(), # sorts them from newest to oldest
            ResumeAnalysis.id.desc() # secondary ordering when timestamps are identical
        )
        .first()
    )

    if latest_analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No saved analysis found for this resume."
        )

    # 4. Return the saved analysis and its metadata.
    return {
        "resume_id": resume.id,
        "title": resume.title or "Untitled resume",
        "model_name": latest_analysis.model_name,
        "created_at": latest_analysis.created_at,
        **latest_analysis.analysis_result # It unpacks the six fields stored in the JSON column into the returned dictionary
    }
