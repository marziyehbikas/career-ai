# Tables structure
                                                                                 # long body of text without specifying a small maximum length
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base() # A class that our database models can inherit from.


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String, default="user")

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    # the name of variables here are what you get when you access the relationship from that particular object.
    # cascade="all, delete-orphan": If a user is deleted the resumes that belong to that user will be deleted too

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    file_path = Column(String)

    user_id = Column(Integer, ForeignKey("users.id", 
                                         ondelete="CASCADE"))
                                        # If a user is deleted the resumes that belong to that user will be deleted too

    user = relationship("User", back_populates="resumes")
                                # back_populate: contains the name of the relationship attribute on the OTHER class
                                # back_populate: The corresponding relationship attribute on the other model is named ..

    analyses = relationship(
    "ResumeAnalysis",
    back_populates="resume",
    cascade="all, delete-orphan",
    passive_deletes=True
    ) # resume.analysis
                        

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True # creates an index that helps the database find analyses belonging to a particular resume more efficiently
    )

    analysis_result = Column(JSON, nullable=False)

    model_name = Column(String(100), nullable=False)
    
    resume_text_snapshot = Column(Text, nullable=True)

    content_hash = Column(String(64), nullable=True)
                          # SHA-256 produces a hexadecimal fingerprint containing exactly 64 characters

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), # current timestamp when a new record is inserted
        nullable=False
    )

    resume = relationship("Resume", back_populates="analyses")