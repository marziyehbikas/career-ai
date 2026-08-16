#Define what API requests and responses should look like

# Each class inherits from BaseModel, which validates incoming data and controls API output format.
from pydantic import BaseModel, Field

# -------------------------
# INPUT SCHEMAS
# -------------------------

# Validate incoming request data

class UserCreate(BaseModel):
    # Id is added automatically
    name: str
    email: str

class UserUpdate(BaseModel):
    # Id is taken from the URL
    name: str
    email: str


class ResumeCreate(BaseModel):
    title: str
    file_path: str
    user_id: int


class ResumeUpdate(BaseModel):
    title: str
    file_path: str
    user_id: int

# -------------------------
# RESOURCE RESPONSE SCHEMAS
# -------------------------

# Describe returned resources

class UserListResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
        # Read values from object attributes instead of dictionary keys.
        # SQLAlchemy object => User(id=1, name="Marzi", email="marzi@example.com")
        # dictionary => {id=1, name="Marzi", email="marzi@example.com"}

class ResumeListResponse(BaseModel):
    id: int
    title: str
    file_path: str

    class Config:
        from_attributes = True


class UserDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    resumes: list[ResumeListResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class ResumeDetailResponse(BaseModel):
    id: int
    title: str
    file_path: str
    user: UserListResponse

    class Config:
        from_attributes = True

# -------------------------
# ACTION RESPONSE SCHEMAS
# -------------------------

# Describe the result of an operation

class UserCreateResponse(BaseModel):
    message: str
    user: UserListResponse

class UserUpdateResponse(BaseModel):
    message: str
    user: UserListResponse

class MessageResponse(BaseModel):
    message: str

class ResumeCreateResponse(BaseModel):
    message: str
    resume: ResumeDetailResponse
