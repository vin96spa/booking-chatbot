import random
import asyncio
from typing import Dict, List, AsyncGenerator
from ._old_openai_services import OpenAIService
from ..utils.prompts import get_escalation_responses


class ResponseManager:
    """Gestisce la logica delle risposte frustranti e simulate durante una conversazione."""

    def __init__(self, openai_service: OpenAIService):
        """
        Inizializza il gestore delle risposte.

        Args:
            openai_service (OpenAIService): Servizio OpenAI per generare contenuti AI.
        """
        self.openai_service = openai_service
        self.frustration_patterns = [
            "transfer_loop",
            "info_request",
            "system_down",
            "callback_promise",
            "wrong_department"
        ]

    async def generate_response_flow(
        self,
        user_message: str,
        session_data: Dict,
        message_count: int,
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Genera un flusso di eventi di risposta basato sul messaggio utente e lo stato della sessione.

        Args:
            user_message (str): Messaggio inviato dall'utente.
            session_data (Dict): Dati relativi alla sessione corrente (es. cronologia).
            message_count (int): Numero di messaggi scambiati finora nella conversazione.

        Yields:
            Dict[str, str]: Eventi della simulazione (es. typing, messaggi, attese).
        """
        frustration_level = min(message_count, 5)
        user_sentiment = await self._analyze_sentiment(user_message)
        pattern = self._choose_frustration_pattern(user_sentiment, frustration_level)

        # Recupera la cronologia della conversazione per il servizio OpenAI
        conversation_history = session_data.get('messages', [])

        async for event in self._execute_pattern(pattern, user_message, session_data, conversation_history, frustration_level):
            yield event

    async def _analyze_sentiment(self, message: str) -> str:
        """
        Analizza in modo semplice il sentimento del messaggio utente.

        Args:
            message (str): Messaggio dell'utente.

        Returns:
            str: Sentimento rilevato ('angry', 'frustrated', 'calm').
        """
        angry_words = ["arrabbiato", "furioso", "assurdo", "ridicolo", "basta"]
        frustrated_words = ["frustrato", "stufo", "impossibile", "perchè", "perché"]

        message_lower = message.lower()

        if any(word in message_lower for word in angry_words):
            return "angry"
        elif any(word in message_lower for word in frustrated_words):
            return "frustrated"
        else:
            return "calm"

    def _choose_frustration_pattern(self, sentiment: str, level: int) -> str:
        """
        Sceglie il pattern di frustrazione da utilizzare in base al sentimento e al livello.

        Args:
            sentiment (str): Sentimento rilevato dall'utente.
            level (int): Livello di frustrazione calcolato in base al numero di messaggi.

        Returns:
            str: Nome del pattern scelto.
        """
        if sentiment == "angry" and level >= 3:
            return "transfer_loop"
        elif level == 1:
            return "openai_response"  # Usa OpenAI per le prime risposte
        else:
            return random.choice(self.frustration_patterns)

    async def _execute_pattern(
        self,
        pattern: str,
        user_message: str,
        session_data: Dict,
        conversation_history: List,
        frustration_level: int
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Esegue il pattern di risposta scelto.

        Args:
            pattern (str): Nome del pattern da eseguire.
            user_message (str): Messaggio dell'utente.
            session_data (Dict): Dati relativi alla sessione corrente.
            conversation_history (List): Cronologia della conversazione.
            frustration_level (int): Livello di frustrazione corrente.

        Yields:
            Dict[str, str]: Eventi della conversazione simulata.
        """
        if pattern == "openai_response":
            async for event in self.openai_service.get_frustration_response(
                user_message,
                conversation_history,
                frustration_level
            ):
                yield event

        elif pattern == "transfer_loop":
            async for event in self._transfer_loop_pattern(user_message):
                yield event

        elif pattern == "info_request":
            async for event in self._info_request_pattern(user_message):
                yield event

        elif pattern == "system_down":
            async for event in self._system_down_pattern():
                yield event

        elif pattern == "callback_promise":
            async for event in self._callback_promise_pattern():
                yield event

        else:
            # Default fallback a OpenAI
            async for event in self.openai_service.get_frustration_response(
                user_message,
                conversation_history,
                frustration_level
            ):
                yield event

    async def _transfer_loop_pattern(
        self,
        user_message: str
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Simula un trasferimento continuo tra reparti (transfer loop).

        Args:
            user_message (str): Messaggio dell'utente.

        Yields:
            Dict[str, str]: Eventi della simulazione (es. trasferimenti, messaggi di attesa).
        """
        departments = [
            "assistenza tecnica",
            "servizio clienti",
            "amministrazione",
            "supporto specializzato",
            "reparto reclami"
        ]

        dept = random.choice(departments)
        yield {"type": "typing", "data": "Sto controllando..."}
        await asyncio.sleep(2)

        yield {"type": "message", "data": f"Perfetto! La trasferisco a {dept}..."}
        yield {"type": "waiting_start", "data": f"transfer_{dept}"}

        await asyncio.sleep(random.uniform(5, 15))

        yield {"type": "waiting_end", "data": ""}
        yield {"type": "message", "data": f"Mi dispiace, {dept} è momentaneamente non disponibile. Posso aiutarla io?"}

    async def _info_request_pattern(
        self,
        user_message: str
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Simula una richiesta di informazioni insolite o frustranti.

        Args:
            user_message (str): Messaggio dell'utente.

        Yields:
            Dict[str, str]: Eventi della simulazione (typing, richiesta assurda).
        """
        info_requests = [
            "Può fornirmi il suo codice fiscale?",
            "Ho bisogno della data di nascita di sua nonna.",
            "Qual è il colore del suo primo animale domestico?",
            "Mi può dire che tempo faceva quando ha fatto l'ultimo acquisto?"
        ]

        yield {"type": "typing", "data": "Certo, la posso aiutare!"}
        await asyncio.sleep(2)
        yield {"type": "message", "data": random.choice(info_requests)}

    async def _system_down_pattern(self) -> AsyncGenerator[Dict[str, str], None]:
        """Simula problemi di sistema."""
        yield {"type": "typing", "data": "Un momento..."}
        await asyncio.sleep(3)
        yield {"type": "message", "data": "Il sistema è temporaneamente in manutenzione. Riprovi tra 24-48 ore."}

    async def _callback_promise_pattern(self) -> AsyncGenerator[Dict[str, str], None]:
        """Simula la promessa di un callback che non arriverà mai."""
        yield {"type": "typing", "data": "Capisco la sua urgenza..."}
        await asyncio.sleep(2)
        yield {"type": "message", "data": "La ricontatteremo entro 5-7 giorni lavorativi (oppure 8-9 se i sindacati indicono sciopero). Grazie per la pazienza!"}