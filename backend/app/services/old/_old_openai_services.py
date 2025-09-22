import asyncio
import json
import random
from typing import AsyncGenerator, Dict, List, Optional
from openai import AsyncOpenAI
from ..utils.prompts import get_system_prompt, get_frustrating_scenarios
import logging


logger = logging.getLogger(__name__)


class OpenAIService:
    """Servizio asincrono per interagire con i modelli OpenAI e simulare conversazioni frustranti."""

    def __init__(self, api_key: str):
        """
        Inizializza il servizio OpenAI.

        Args:
            api_key (str): Chiave API valida per accedere al client OpenAI.
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    async def get_frustration_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        frustration_level: int = 1
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Genera una risposta frustrante in base al messaggio dell'utente e al livello di frustrazione.

        Simula una digitazione iniziale, sceglie casualmente se rispondere subito
        in modo frustrante o prima in modo utile e poi frustrante.

        Args:
            user_message (str): Messaggio attuale dell'utente.
            conversation_history (List[Dict[str, str]]): Cronologia della conversazione (ultimi messaggi).
            frustration_level (int, optional): Livello di frustrazione da applicare al sistema. Default = 1.

        Yields:
            Dict[str, str]: Eventi della conversazione (typing, messaggi chunk, errori, ecc.).
        """
        try:
            #yield {"type": "typing", "data": "prova 1"}
            #await asyncio.sleep(random.uniform(1, 3))

            system_prompt = get_system_prompt(frustration_level)
            messages = self._build_conversation(system_prompt, conversation_history, user_message)

            should_be_immediately_frustrating = random.choice([True, False])

            if should_be_immediately_frustrating:
                async for chunk in self._get_ai_response_stream(messages):
                    yield {"type": "message_chunk", "data": chunk}
            else:
                async for event in self._simulate_helpful_then_frustrating(user_message, messages):
                    yield event

        except Exception as e:
            logger.error(f"Errore Openai service: {e}")
            yield {"type": "Error", "data": "Mi dispiace, c'è un problema tecnico. La ricontatterò al più presto!"}

    async def _simulate_helpful_then_frustrating(
        self,
        user_message: str,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Simula una conversazione che inizia utile e si conclude in modo frustrante.

        - Risponde inizialmente in modo professionale e conciso.
        - Simula un trasferimento della chiamata.
        - Dopo un'attesa casuale, restituisce uno scenario frustrante.

        Args:
            user_message (str): Messaggio dell’utente.
            messages (List[Dict[str, str]]): Lista di messaggi accumulati nella conversazione.

        Yields:
            Dict[str, str]: Eventi della simulazione (risposte utili, trasferimento, scenari frustranti).
        """
        helpful_prompt = (
            "Rispondi in modo professionale e disponibile, "
            "come se stessi per aiutare davvero il cliente. "
            "Sii molto breve (max 2 frasi)."
        )

        helpful_messages = messages + [{"role": "user", "content": helpful_prompt}]

        async for chunk in self._get_ai_response_stream(helpful_messages):
            yield {"type": "message_chunk", "data": chunk}

        await asyncio.sleep(1)

        # Fake transfer
        transfer_messages = [
            "La trasferisco immediatamente al reparto competente...",
            "Un momento, la collego con il supervisor...",
            "La metto in contatto con un esperto..."
        ]

        yield {"type": "message", "data": random.choice(transfer_messages)}
        yield {"type": "waiting_start", "data": "transfer"}

        await asyncio.sleep(random.uniform(15, 45))

        frustrating_scenarios = get_frustrating_scenarios()
        scenario = random.choice(frustrating_scenarios)

        yield {"type": "waiting_end", "data": ""}
        yield {"type": "message", "data": scenario}

    async def _get_ai_response_stream(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """
        Ottiene la risposta del modello AI come stream di chunk di testo.

        Args:
            messages (List[Dict[str, str]]): Lista di messaggi della conversazione, inclusi system e user.

        Yields:
            str: Parti (chunk) della risposta generata dal modello.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                max_tokens=50, #limita il num di token che il modello genera. utile per non sprecare credito dell'API
                temperature=0.8,
            )

            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Errore Openai service: {e}")
            yield "Mi dispiace, ce un problema tecnico."

    def _build_conversation(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        current_message: str
    ) -> List[Dict[str, str]]:
        """
        Costruisce la lista dei messaggi della conversazione da passare al modello AI.

        Args:
            system_prompt (str): Prompt di sistema basato sul livello di frustrazione.
            history (List[Dict[str, str]]): Cronologia della conversazione (ultimi 10 messaggi).
            current_message (str): Messaggio attuale dell'utente.

        Returns:
            List[Dict[str, str]]: Lista completa dei messaggi (system, history, current).
        """
        messages = [{"role": "system", "content": system_prompt}]

        # Handle None history gracefully
        if history is None:
            history = []
        
        for msg in history[-10:]:
            messages.append(msg)

        messages.append({"role": "user", "content": current_message})
        return messages

    async def get_contextual_music(self, user_sentiment: str) -> str:
        """
        Restituisce un brano musicale in base al sentimento dell’utente.

        (Da implementare)

        Args:
            user_sentiment (str): Sentimento dell’utente (es. 'felice', 'triste').

        Returns:
            str: Titolo o riferimento a un brano musicale.
        """
        pass
