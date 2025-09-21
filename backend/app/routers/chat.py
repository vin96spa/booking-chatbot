import logging

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import uuid
import asyncio

from ..services.session_manager import SessionManager
from ..models.chat_models import ChatMessage, ChatResponse

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

session_manager = SessionManager()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@router.post("/chat1")
async def start_chat(request: ChatRequest, app_request: Request):
    try:
        # Recupera o crea sessione
        if request.session_id:
            # Usa session_id esistente
            session_id = request.session_id
            session_data = session_manager.get_or_create_session(session_id)
        else:
            # Crea nuovo session_id
            session_id = str(uuid.uuid4())
            session_data = session_manager.get_or_create_session(session_id)

        session_data["message_count"] = session_data.get("message_count", 0) + 1

        logger.debug(f"PRIMA di salvare USER message:")
        logger.debug(f"Session {session_id} - Messages count: {len(session_data.get('messages', []))}")
        for i, msg in enumerate(session_data.get('messages', [])):
            logger.debug(f"  {i}: {msg['role']} - {msg['content'][:50]}...")

        # Salva messaggio utente
        session_manager.add_message(session_id, "user", request.message)

        logger.debug(f"DOPO aver salvato USER message:")
        logger.debug(f"Session {session_id} - Messages count: {len(session_data.get('messages', []))}")
        for i, msg in enumerate(session_data.get('messages', [])):
            logger.debug(f"  {i}: {msg['role']} - {msg['content'][:50]}...")

        # Response manager preso da app.state
        response_manager = app_request.app.state.response_manager

        async def generate_sse_stream():
            try:
                # Manda subito session_id al client
                yield f"data: {json.dumps({'type': 'session_id', 'data': session_id})}\n\n"

                # Variabile per accumulare la risposta completa dell'assistant
                complete_response = ""

                # Genera risposta step by step
                async for event in response_manager.generate_response_flow(
                        request.message,
                        session_data,
                        session_data["message_count"],
                ):
                    # Accumula i chunk di messaggio per salvarli alla fine
                    if event.get('type') == 'message_chunk':
                        complete_response += event.get('data', '')
                    elif event.get('type') == 'message':
                        complete_response += event.get('data', '')

                    yield f"data: {json.dumps(event)}\n\n"
                    await asyncio.sleep(0.1)

                logger.debug(f"PRIMA di salvare ASSISTANT response:")
                logger.debug(f"Complete response length: {len(complete_response)}")
                logger.debug(f"Complete response content: '{complete_response[:100]}...'")
                logger.debug(f"Session {session_id} - Messages count PRIMA: {len(session_data.get('messages', []))}")
                for i, msg in enumerate(session_data.get('messages', [])):
                    logger.debug(f"  {i}: {msg['role']} - {msg['content'][:50]}...")


                # Salva la risposta completa dell'assistant nella sessione
                if complete_response.strip():
                    session_manager.add_message(session_id, "assistant", complete_response.strip())

                    logger.debug(f"DOPO aver salvato ASSISTANT response:")
                    session_data_final = session_manager.get_session(session_id)
                    logger.debug(
                        f"Session {session_id} - Messages count DOPO: {len(session_data_final.get('messages', []))}")
                    for i, msg in enumerate(session_data_final.get('messages', [])):
                        logger.debug(f"  {i}: {msg['role']} - {msg['content'][:50]}...")


                # Notifica di completamento
                yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"
                yield "event: close\ndata: {}\n\n"

            except Exception as e:
                error_event = {
                    "type": "error",
                    "data": f"Errore interno: {str(e)}",
                }
                yield f"data: {json.dumps(error_event)}\n\n"

        return StreamingResponse(
            generate_sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella chat: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        if session_id in session_manager.sessions:
            return session_manager.sessions[session_id]
        else:
            raise HTTPException(status_code=404, detail="Sessione non trovata")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore recupero sessione: {str(e)}")


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    success = session_manager.clear_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    return {"message": "Sessione cancellata con successo"}


@router.get("/debug/sessions")
async def get_all_sessions():
    return session_manager.get_all_sessions()