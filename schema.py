# Define what API requests and responses should look like

# Each class inherits from BaseModel, which validates incoming data and controls API output format.
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

# -------------------------
# INPUT SCHEMAS
# -------------------------

# Validate incoming request data

class UserCreate(BaseModel):
    # Id is added automatically
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    # Id is taken from the URL
    name: str
    email: str

class UserLogin(BaseModel):
    email: str
    password: str

class RoleUpdate(BaseModel):
    role: Literal["user", "admin"]
    # Restrict values to only valid roles like "user" and "admin"

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# -------------------------
# RESPONSE SCHEMAS
# -------------------------

# Describe returned resources

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class UserPaginationResponse(BaseModel):
    page: int
    limit: int
    total_users: int
    total_pages: int
    data: list[UserResponse]

    class Config:
        from_attributes = True
        # Read values from object attributes instead of dictionary keys.
        # SQLAlchemy object => User(id=1, name="Marzi", email="marzi@example.com")
        # dictionary => {id=1, name="Marzi", email="marzi@example.com"}

class ResumeResponse(BaseModel):
    id: int
    title: str
    file_path: str

    class Config:
        from_attributes = True


class UserDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    resumes: list[ResumeResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class ResumeDetailResponse(BaseModel):
    id: int
    title: str
    file_path: str
    user: UserResponse

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user: UserResponse

class AdminUserData(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class AdminUserResponse(BaseModel):
    message: str
    user: AdminUserData

class ResumeTextResponse(BaseModel):
    resume_id: int
    title: str
    extracted_text: str
    character_count: int

class ResumeAnalysisResponse(BaseModel):
    # Analysing a resume return response
    resume_id: int
    title: str
    summary: str
    strengths: list[str]
    areas_for_improvement: list[str]
    detected_skills: list[str]
    missing_or_unclear_information: list[str]
    recommendations: list[str]

class SavedResumeAnalysisResponse(BaseModel):
    # Save the analysis in the DB response
    resume_id: int
    title: str
    model_name: str
    created_at: datetime

    summary: str
    strengths: list[str]
    areas_for_improvement: list[str]
    detected_skills: list[str]
    missing_or_unclear_information: list[str]
    recommendations: list[str]

# -------------------------
# ACTION RESPONSE SCHEMAS
# -------------------------

# Describe the result of an operation

class UserCreateResponse(BaseModel):
    message: str
    user: UserResponse

class UserUpdateResponse(BaseModel):
    message: str
    user: UserResponse

class MessageResponse(BaseModel):
    message: str

class ResumeCreateResponse(BaseModel):
    message: str
    resume: ResumeDetailResponse

class ResumeUpdateResponse(BaseModel):
    message: str
    resume: ResumeDetailResponse


