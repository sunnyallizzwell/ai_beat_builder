from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import math_engine, ai_engine
import os

app = FastAPI(title="Beat Composer API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

os.makedirs('/app/shared_outputs', exist_ok=True)

# Attach the generation engines
app.include_router(math_engine.router, prefix="/api/math", tags=["Math Engine"])
app.include_router(ai_engine.router, prefix="/api/ai", tags=["AI Engine"])

@app.get("/")
def health():
    return {"status": "Composer Backend Online"}