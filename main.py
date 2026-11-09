from fastapi import FastAPI
from routers import users, resumes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Communicate with the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(resumes.router)

@app.get("/")
def get_home():
    return {"message": "Backend Career API is running"}

@app.get("/health")
def get_health():
    return {"message": "Status OK"}

