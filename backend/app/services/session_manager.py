from typing import Dict, List, Optional, Any
import time
import random
from datetime import datetime, timedelta


class SessionManager:
    """Gestisce le sessioni utente con timeout, cronologia dei messaggi e stato contestuale."""

    def __init__(self):
        """
        Inizializza il gestore delle sessioni.

        Attributi:
            sessions (Dict[str, Dict[str, Any]]): Dizionario contenente tutte le sessioni attive.
            session_timeout (int): Tempo massimo di inattività in secondi prima della scadenza di una sessione (default = 3600s).
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """
        Recupera una sessione esistente o ne crea una nuova.

        Args:
            session_id (str): Identificativo univoco della sessione.

        Returns:
            Dict[str, Any]: Dati relativi alla sessione (id, timestamps, messaggi, ecc.).
        """
        current_time = time.time()

        if session_id in self.sessions:
            self.sessions[session_id]['last_access'] = current_time
            return self.sessions[session_id]

        self.sessions[session_id] = {
            'session_id': session_id,
            'created_at': current_time,
            'last_access': current_time,
            'messages': [],
            'message_count': 0,
            'frustration_level': 1,
            'context': {}
        }
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Restituisce i dati di una sessione.

        Args:
            session_id (str): Identificativo univoco della sessione.

        Returns:
            Optional[Dict[str, Any]]: Dati della sessione o None se non esiste.
        """
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Aggiunge un messaggio alla cronologia di una sessione.

        Args:
            session_id (str): Identificativo della sessione.
            role (str): Ruolo del messaggio ('user' o 'assistant').
            content (str): Contenuto testuale del messaggio.

        Returns:
            bool: True se il messaggio è stato aggiunto, False se la sessione non esiste.
        """
        if session_id not in self.sessions:
            return False

        message = {
            'role': role,
            'content': content,
            'timestamp': time.time(),
        }

        frustration = random.randint(1, 6) # Simula il cambiamento del livello di frustrazione
        print(f"Nuovo livello di frustrazione: {frustration}")
        self.sessions[session_id]['frustration_level'] = frustration  
        self.sessions[session_id]['messages'].append(message)

        # Mantieni solo gli ultimi 50 messaggi per performance
        if len(self.sessions[session_id]['messages']) > 50:
            self.sessions[session_id]['messages'] = self.sessions[session_id]['messages'][-50:]

        # Aggiorna il timestamp di ultimo accesso
        self.sessions[session_id]['last_access'] = time.time()

        return True

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Restituisce la cronologia recente della conversazione.

        Args:
            session_id (str): Identificativo della sessione.

        Returns:
            List[Dict[str, str]]: Lista degli ultimi 20 messaggi registrati.
        """
        if session_id not in self.sessions:
            return []
        messages = self.sessions[session_id]['messages']
        return messages[-20:]

    def clear_session(self, session_id: str) -> bool:
        """
        Elimina una sessione.

        Args:
            session_id (str): Identificativo della sessione da eliminare.

        Returns:
            bool: True se la sessione è stata eliminata, False se non esisteva.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """
        Rimuove tutte le sessioni scadute in base al timeout.

        Returns:
            int: Numero di sessioni eliminate.
        """
        current_time = time.time()
        expired_sessions = []

        for session_id, session_data in self.sessions.items():
            if current_time - session_data['last_access'] > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        return len(expired_sessions)

    def get_all_sessions(self) -> Dict[str, Any]:
        """
        Restituisce una panoramica di tutte le sessioni attive.

        Returns:
            Dict[str, Any]: Informazioni generali sulle sessioni (conteggio, id attivi, dettagli).
        """
        return {
            'total_sessions': len(self.sessions),
            'sessions': list(self.sessions.keys()),
            'details': self.sessions
        }