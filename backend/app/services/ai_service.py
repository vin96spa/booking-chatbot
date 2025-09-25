import google.generativeai as genai
from openai import OpenAI

from abc import ABC, abstractmethod
from ..utils.prompts import get_system_prompt, get_frustrating_scenarios
from ..models.chat_models import GeminiChatMessage, OpenAIChatMessage

class AiService(ABC):

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
    system_instruction = get_system_prompt(frustration)
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
    system_instruction = get_system_prompt(frustration)
    contents = [OpenAIChatMessage(role="system", content=system_instruction).__dict__]
    contents.extend(messages)

    response = self.client.chat.completions.create(
      model=self.model,
      max_tokens=100,
      temperature=0.8,
      messages=contents, 
    )

    ai_msg = response.choices[0].message.content

    return ai_msg