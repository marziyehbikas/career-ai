#Create connection file (Tell Python how to connect to PostgreSQL)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:Marzi%401234@localhost:5432/career_ai";

engine = create_engine(DATABASE_URL) # connects to the DB

# Creats a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine # The sessions created by this factory should use this engine to communicate with the database.
)

# -------------------------
# OPEN AND CLOSE DB AUTOMATICALLY
# -------------------------

def get_db():
    db = SessionLocal() # Creats a session/conversation 
    try:
        yield db
    finally:
        db.close()