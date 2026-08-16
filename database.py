#Create connection file (Tell Python how to connect to PostgreSQL)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:Marzi%401234@localhost:5432/career_ai";

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -------------------------
# OPEN AND CLOSE DB AUTOMATICALLY
# -------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()