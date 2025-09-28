import random
import google.generativeai as genai
from openai import OpenAI

from abc import ABC, abstractmethod
from ..utils.prompts import get_system_prompt, get_frustrating_scenarios
from ..models.chat_models import GeminiChatMessage, OpenAIChatMessage

class AiService(ABC):

  def compose_instructions(self, frustration) -> str:
    """
      Recupera il prompt per istruire l'AI. 
      In modo casuale potrebbe essere aggiunto al prompt uno specifico scenario di frustrazione.

      Returns:
          str: Le istruzioni per il sistema AI.
      """
    system_instruction = get_system_prompt(frustration)
    frustration_scenarios = get_frustrating_scenarios()

    n_scenarios = len(frustration_scenarios)-1
    index = random.randint(0, n_scenarios + 6)
    print(f"frustration scenarios index: {index}") # x TEST e log

    if index <= n_scenarios:
      system_instruction += " Quando il contesto è adatto, usa frasi come '" + frustration_scenarios[index] + "'."

    return system_instruction

  @abstractmethod
  def send_message(self, frustration, messages):
    pass


class GeminiService(AiService):

  def __init__(self, api_key: str):
    self.client = genai.configure(api_key=api_key)
    self.model = 'gemini-2.0-flash-exp' # 'gemini-2.0-flash-exp' o 'gemini-1.5-flash'
    self.config = genai.types.GenerationConfig(
      max_output_tokens=100,
      temperature=0.8
    )

  def send_message(self, frustration, messages):
    system_instruction = self.compose_instructions(frustration)
    model = genai.GenerativeModel(self.model, generation_config=self.config, system_instruction=system_instruction)
    
    response = model.generate_content(contents=messages)
    ai_msg = response.text
    print(f"prompt: {system_instruction}") # x TEST e log

    return ai_msg
  
class OpenAIService(AiService):

  def __init__(self, api_key: str):    
    print(f"api_key: {api_key}")
    self.client = OpenAI(api_key=api_key)
    self.model = "gpt-4o-mini"  # "gpt-4o-mini" o "gpt-3.5-turbo"

  def send_message(self, frustration, messages):
    system_instruction = self.compose_instructions(frustration)
    contents = [OpenAIChatMessage(role="system", content=system_instruction).__dict__]
    contents.extend(messages)
    
    print(f"prompt: {system_instruction}") # x TEST e log

    response = self.client.chat.completions.create(
      model=self.model,
      max_tokens=100,
      temperature=0.8,
      messages=contents, 
    )

    ai_msg = response.choices[0].message.content

    return ai_msg