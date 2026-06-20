"""
FastAPI backend for ClinicalTrialCompass
"""

import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import PatientProfile, MatchResponse
from pipeline import run_pipeline
from vector_store import VectorStore

# Load environment variables from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

app = FastAPI(
    title="ClinicalTrialCompass",
    description="AI-powered clinical trial matching"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector store
vector_store = VectorStore(path=CHROMA_PATH)


@app.get("/health")
async def health():
    """Health check endpoint"""
    trial_count = vector_store.count()
    if trial_count == 0:
        raise HTTPException(
            status_code=503,
            detail="No trials indexed. Run ingest.py first."
        )
    
    return {
        "status": "ok",
        "trials_indexed": trial_count
    }


@app.post("/match")
async def match(profile: PatientProfile):
    """
    Match a patient to relevant clinical trials
    
    Request body: PatientProfile (JSON)
    Returns: MatchResponse with top 5 matching trials
    """
    try:
        # Check if data is indexed
        if vector_store.count() == 0:
            raise HTTPException(
                status_code=503,
                detail="No trials indexed. Run ingest.py first."
            )
        
        print(f"\n--- Processing match request ---")
        print(f"Patient: {profile.primary_diagnosis}, {profile.age}yo")
        
        start_time = time.time()
        
        # Run the 3-pass pipeline
        matches = run_pipeline(profile)
        
        elapsed = time.time() - start_time
        print(f"Match completed in {elapsed:.2f}s")
        
        response = MatchResponse(
            patient_profile=profile,
            matches=matches
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /match endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing match: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
