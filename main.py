from fastapi import FastAPI
from routers import users, resumes


app = FastAPI()

app.include_router(users.router)
app.include_router(resumes.router)

@app.get("/")
def get_home():
    return {"message": "Backend Career API is running"}

@app.get("/health")
def get_health():
    return {"message": "Status OK"}

