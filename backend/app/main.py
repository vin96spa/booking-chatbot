from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import os
import uuid
import asyncio

#from .routers.old import _old_chat
#from .services.old._old_openai_services import OpenAIService as OpenAIServiceOpenAI
#from .services.old._old_gemini_services import OpenAIService as OpenAIServiceGemini
#from .services.old._old_response_manager import ResponseManager
from .services.session_manager import SessionManager
from .services.ai_service import AiService, GeminiService, OpenAIService
from .models.chat_models import ChatRequest
from fastapi import HTTPException

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza il servizio AI e lo salva nello stato dell'app
    ai_service = get_ai_service("GEMINI_API_KEY") # OPENAI_API_KEY o GEMINI_API_KEY
    app.state.ai_service = ai_service
    print(f"Usando servizio AI: {type(ai_service).__name__}")

    #openai_key = os.getenv("OPENAI_API_KEY")
    #gemini_key = os.getenv("GEMINI_API_KEY")
    #print(f"lifespan context manager avviato")

    #if not openai_key or not gemini_key:
    #    raise Exception("Nessuna API key trovata. Imposta OPENAI_API_KEY o GEMINI_API_KEY nel .env")

    # Scegli provider (commenta quello che non usi)
    #openai_service = OpenAIServiceOpenAI(api_key=openai_key)
    #response_manager = ResponseManager(openai_service)

    #gemini_service = OpenAIServiceGemini(api_key=gemini_key)
    #response_manager = ResponseManager(gemini_service)

    # Iniettiamo i servizi nello state dell’app
    #app.state.openai_service = openai_service
    #app.state.gemini_service = gemini_service
    #app.state.response_manager = response_manager

    yield

    # Chiusura risorse app
    ai_service = None



def get_ai_service(api_key: str) -> AiService:
    print(f"get service per {api_key}")
    """
    Recupera il servizio AI per la chiave API fornita.
    """
    key = os.getenv(api_key)
    if not key:
        raise Exception("Nessuna API key trovata. Imposta OPENAI_API_KEY o GEMINI_API_KEY nel .env")
    
    ai_service = None
    if api_key == "GEMINI_API_KEY":
        ai_service = GeminiService(key)

    else:
        ai_service = OpenAIService(key)

    if not ai_service:
        raise Exception(f"Servizio AI non disponibile")

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
#app.include_router(chat.router, prefix="/api", tags=["chat"])


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
    ai_service = app.state.ai_service
    current_session = session_manager.get_session(request.session_id)
    session_manager.add_message(request.session_id, "user", request.message)
    frustration = current_session["frustration_level"]
    print(f"frustration level: {frustration}")
    response = ai_service.send_message(request.message, frustration)
    session_manager.add_message(request.session_id, "assistant", response)

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
    
@app.delete("/api/close_chat/{session_id}")
async def close_chat(session_id: str):
    print(f"Chiusura chat, session_id: {session_id}")
    if session_manager.clear_session(session_id):
        return {"detail": f"Sessione {session_id} cancellata."}
    else:
        raise HTTPException(status_code=404, detail="Sessione non trovata.")