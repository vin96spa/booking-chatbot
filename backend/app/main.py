from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .routers import chat
from .services.openai_services import OpenAIService as OpenAIServiceOpenAI
from .services.gemini_services import OpenAIService as OpenAIServiceGemini
from .services.response_manager import ResponseManager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("OPENAI_API_KEY")
    api_key2 = os.getenv("GEMINI_API_KEY")

    if not api_key and not api_key2:
        raise Exception("Nessuna API key trovata. Imposta OPENAI_API_KEY o GEMINI_API_KEY nel .env")

    # Scegli provider (commenta quello che non usi)
    openai_service = OpenAIServiceOpenAI(api_key=api_key)
    response_manager = ResponseManager(openai_service)

    #gemini_service = OpenAIServiceGemini(api_key=api_key2)
    #response_manager = ResponseManager(gemini_service)

    # Iniettiamo i servizi nello state dell’app
    app.state.openai_service = openai_service
    #app.state.gemini_service = gemini_service
    app.state.response_manager = response_manager

    yield


app = FastAPI(
    title="Frustrating Chatbot API",
    description="Il chatbot di prenotazione più frustrante al mondo",
    version="1.0",
    lifespan=lifespan,
)

# Config CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router, prefix="/api", tags=["chat"])


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "frustrating-bot"}


@app.get("/")
async def root():
    return {"message": "Frustrating Chatbot API v1.0"}
