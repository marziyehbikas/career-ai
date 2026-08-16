#create the actual table inside the database

from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

print("Tables created!")