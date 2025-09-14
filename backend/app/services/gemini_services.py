import asyncio
import json
import random
from typing import AsyncGenerator, Dict, List, Optional
import google.generativeai as genai
from ..utils.prompts import get_system_prompt, get_frustrating_scenarios
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # o 'gemini-1.5-flash'

    async def get_frustration_response(self,
                                       user_message: str,
                                       conversation_history: List[Dict[str, str]],
                                       frustration_level: int = 1
                                       ) -> AsyncGenerator[Dict[str, str], None]:
        try:
            yield {"type": "typing", "data": "L'operatore sta digitando..."}
            await asyncio.sleep(random.uniform(1, 3))

            system_prompt = get_system_prompt(frustration_level)
            messages = self._build_conversation(system_prompt, conversation_history, user_message)

            should_be_immediately_frustrating = random.choice([True, False])

            if should_be_immediately_frustrating:
                async for chunk in self._get_ai_response_stream(messages):
                    yield {"type": "message_chunk", "data": chunk}
            else:
                async for response in self._simulate_helpful_then_frustrating(user_message, messages):
                    yield response

        except Exception as e:
            logger.error(f"Errore Gemini service: {e}")
            yield {"type": "error", "data": "Mi dispiace, c'è un problema tecnico. La ricontatterò al più presto!"}

    async def _simulate_helpful_then_frustrating(self,
                                                 user_message: str,
                                                 messages: List[Dict[str, str]]
                                                 ) -> AsyncGenerator[Dict[str, str], None]:
        """Simulate helpful: first help than transfer call and frustration"""

        helpful_prompt = """Rispondi in modo professionale e disponibile,
        come se stessi per aiutare davvero il cliente. Sii molto breve(max 2 frasi)."""

        # Per Gemini, aggiungiamo il prompt helpful al messaggio dell'utente
        helpful_messages = messages[:-1] + [{"role": "user", "content": f"{user_message}\n\n{helpful_prompt}"}]

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

    async def _get_ai_response_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        try:
            # Converti i messaggi nel formato Gemini
            gemini_messages = self._convert_to_gemini_format(messages)

            response = await asyncio.to_thread(
                self.model.generate_content,
                gemini_messages,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=150,
                    temperature=0.8,
                )
            )

            # Gemini non ha streaming asincrono nativo, simuliamo lo streaming
            full_text = ""
            async for chunk in self._simulate_streaming(response):
                if chunk:
                    yield chunk

        except Exception as e:
            logger.error(f"Errore Gemini service: {e}")
            yield "Mi dispiace, c'è un problema tecnico."

    async def _simulate_streaming(self, response) -> AsyncGenerator[str, None]:
        """Simula lo streaming per Gemini dividendo la risposta in chunks"""
        try:
            # Ottieni il testo completo
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text

            # Simula lo streaming dividendo il testo
            words = full_text.split()
            current_chunk = ""

            for word in words:
                current_chunk += word + " "
                if len(current_chunk) > 10:  # Invia chunk ogni ~10 caratteri
                    yield current_chunk
                    current_chunk = ""
                    await asyncio.sleep(0.05)  # Piccola pausa per simulare streaming

            if current_chunk.strip():
                yield current_chunk

        except Exception as e:
            logger.error(f"Errore simulazione streaming: {e}")
            yield "Errore nella generazione della risposta."

    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> str:
        """Converte i messaggi dal formato OpenAI al formato Gemini"""
        formatted_messages = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                formatted_messages.append(f"Sistema: {content}")
            elif role == "user":
                formatted_messages.append(f"Utente: {content}")
            elif role == "assistant":
                formatted_messages.append(f"Assistente: {content}")

        return "\n\n".join(formatted_messages)

    def _build_conversation(self,
                            system_prompt: str,
                            history: List[Dict[str, str]],
                            current_message: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}]

        for msg in history[-10:]:
            messages.append(msg)

        messages.append({"role": "user", "content": current_message})
        return messages

    async def get_contextual_music(self, user_sentiment: str) -> str:
        pass