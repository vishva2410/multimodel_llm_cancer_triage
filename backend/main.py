from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OncoDetect X API", version="1.0.0", description="AI-assisted cancer triage and decision-support system API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "OncoDetect X API is running", "status": "System Operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from app.api.default_routes import router as default_router
from app.api.routes import analysis

app.include_router(default_router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
