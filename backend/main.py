from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
from routers import ripper

app = FastAPI(title="Crate Digger Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach the ripper endpoints to the main API
app.include_router(ripper.router, prefix="/api/ripper", tags=["Ripper"])

@app.get("/")
def health_check():
    return {"status": "online", "message": "Crate Digger Backend is running."}