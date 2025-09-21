from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import os
import uuid
import asyncio

from .routers import chat
from .services.openai_services import OpenAIService as OpenAIServiceOpenAI
from .services.gemini_services import OpenAIService as OpenAIServiceGemini
from .services.response_manager import ResponseManager
from .services.ai_service import AiService, GeminiService, OpenAIService
from .services.session_manager import SessionManager
from .models.chat_models import ChatRequest
from fastapi import HTTPException

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("OPENAI_API_KEY")
    api_key2 = os.getenv("GEMINI_API_KEY")

    if not api_key and not api_key2:
        raise Exception("Nessuna API key trovata. Imposta OPENAI_API_KEY o GEMINI_API_KEY nel .env")

    # Scegli provider (commenta quello che non usi)
    #openai_service = OpenAIServiceOpenAI(api_key=api_key)
    #response_manager = ResponseManager(openai_service)

    gemini_service = OpenAIServiceGemini(api_key=api_key2)
    response_manager = ResponseManager(gemini_service)

    # Iniettiamo i servizi nello state dell’app
    #app.state.openai_service = openai_service
    app.state.gemini_service = gemini_service
    app.state.response_manager = response_manager

    yield



def get_service(api_key: str) -> AiService:
    """
    Recupera il servizio AI per la chiave API fornita.
    """
    key = os.getenv(api_key)
    ai_service = None
    if api_key == "GEMINI_API_KEY":
        ai_service = GeminiService(key)

    else:
        ai_service = OpenAIService(key)
    
    return ai_service

app = FastAPI(
    title="Frustrating Chatbot API",
    description="Il chatbot di prenotazione più frustrante al mondo",
    version="1.0",
    lifespan=lifespan,
)

session_manager = SessionManager()

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


@app.get("/api/start_chat")
async def start_chat():
  # Crea nuovo session_id
  session_id = str(uuid.uuid4())
  print(f"Nuova chat, session_id: {session_id}")
  session_manager.get_or_create_session(session_id)

  return session_id

@app.post("/api/chat")
async def get_response(request: ChatRequest):
  await asyncio.sleep(0.5)  # 500ms di pausa

  try:
    ai_service = get_service("GEMINI_API_KEY") # OPENAI_API_KEY o GEMINI_API_KEY
    print(f"Usando servizio AI: {type(ai_service).__name__}")
    current_session = session_manager.get_session(request.session_id)
    frustration = current_session["frustration_level"]
    print(f"frustration level: {frustration}")
    response = ai_service.send_message(request.message, frustration)
    session_manager.add_message(request.session_id, "user", response)

    return {"role": "assistant", "content": response}
  
  except Exception as e:
    if "quota" in str(e).lower() or "limit" in str(e).lower():
        raise HTTPException(status_code=429, detail="Limite API raggiunto. Riprova tra qualche minuto.")
    elif "network" in str(e).lower():
        raise HTTPException(
            status_code=503,  # Servizio non disponibile
            detail="Problema di connessione al servizio AI."
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Errore temporaneo del server. Riprova tra poco."
        )