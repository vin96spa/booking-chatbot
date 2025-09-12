from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Frustrating Chatbot API")

# CORS configuration per Vercel
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "https://*.vercel.app",  # Preview deployments
        "https://your-domain.com",  # Produzione
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check importante per Railway
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "frustrating-bot"}

@app.get("/")
async def root():
    return {"message": "Frustrating Chatbot API v1.0"}

# ... resto del codice API