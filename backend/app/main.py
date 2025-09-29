from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import os
import uuid

from .services.session_manager import SessionManager
from .services.ai_service import AiService, GeminiService, OpenAIService
from .models.chat_models import AiModel, ChatRequest
from .utils.prompts import get_waiting_words, get_transfer_words
from fastapi import HTTPException

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza il servizio AI e lo salva nello stato dell'app
    ai_service = get_ai_service("OPENAI_API_KEY") # <-- DECIDI QUI SE VUOI USARE "OPENAI_API_KEY" o "GEMINI_API_KEY"
    app.state.ai_service = ai_service

    service_name = type(ai_service).__name__
    print(f"Usando servizio AI: {service_name}")

    if service_name == "GeminiService":
        app.state.ai_model = AiModel.GEMINI
    else:
        app.state.ai_model = AiModel.OPENAI

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


@app.get("/")
async def root():
    return {"message": "Frustrating Chatbot API v1.0"}


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "frustrating-bot"}


@app.get("/api/start_chat")
async def start_chat():
  # Crea nuovo session_id
  session_id = str(uuid.uuid4())
  print(f"Nuova chat, session_id: {session_id}")
  session_manager.get_or_create_session(session_id)

  return {"session_id": session_id}


@app.post("/api/chat")
async def get_response(request: ChatRequest):

  try:
    ai_service = app.state.ai_service

    # Recupera la sessione corrente
    current_session = session_manager.get_session(request.session_id)

    # Aggiunge il messaggio dell'utente alla cronologia della sessione
    session_manager.add_message(request.session_id, "user", request.message, app.state.ai_model)

    frustration = current_session["frustration_level"]
    print(f"frustration level: {frustration}") # x TEST e log

    # Invia la cronologia dei messaggi all'AI
    history = session_manager.get_conversation_history(request.session_id)
    response = ai_service.send_message(frustration, history)
    print(f"history + message: {history}") # x TEST e log
    print(f"AI response: {response}") # x TEST e log

    waiting = False
    # keywords del messaggio dell'assistente che kickstartano l'attesa
    if not "?" in response: 
    # gestione edge case di bot che fa domanda a user e non dev'essere ancora messo in attesa
        for word in get_waiting_words():
            if word in response.lower():
                waiting = True
                break
    print(f"waiting: {waiting}") # x TEST e log

    transfer = False
    # keywords del messaggio dell'assistente che kickstartano il trasferimento
    if not "?" in response: # gestione edge case di bot che fa domanda a user e non dev'essere ancora trasferito
        for word in get_transfer_words():
            if word in response.lower():
                transfer = True
                break
    print(f"transfer: {transfer}") # x TEST e log

    if transfer == True and waiting == True: 
    #gestione edge case di prompt con sia kw trasferimento e kw attesa
        transfer = False
        waiting = False
        print(f"edge case both transfer and waiting = True. New values: ") # x TEST e log
        print(f"transfer: {transfer}")
        print(f"waiting: {waiting}")
        
    funny_personality = False
    if frustration >= 3:
        funny_personality = True
    print(f"funny_personality: {funny_personality}") # x TEST e log
    
    role = "assistant"
    if app.state.ai_model == AiModel.GEMINI:
        role = "model"

    # Aggiunge il messaggio dell'AI alla cronologia della sessione
    session_manager.add_message(request.session_id, role, response, app.state.ai_model)
    
    return {"role": "assistant", "content": response, "waiting": waiting, "transfer": transfer, "funny_personality": funny_personality}
  
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