import google.generativeai as genai
from openai import OpenAI, AsyncOpenAI
import logging

from ..utils.prompts import get_system_prompt, get_frustrating_scenarios
from abc import ABC, abstractmethod

class AiService(ABC):

  @abstractmethod
  def send_message(self, message, frustration):
    pass


class GeminiService(AiService):

  def __init__(self, api_key: str):
    genai.configure(api_key=api_key)
    config = genai.types.GenerationConfig(
      max_output_tokens=100,
      temperature=0.8,
    )
    self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config=config)  # 'gemini-2.0-flash-exp' o 'gemini-1.5-flash'


  def send_message(self, message, frustration):
    system_instruction = get_system_prompt(frustration)
    self.model.system_instruction = system_instruction
    response = self.model.generate_content(contents=message)
    ai_msg = response.text

    return ai_msg
  
class OpenAIService(AiService):

  def __init__(self, api_key: str):    
    print(f"api_key: {api_key}")
    self.client = OpenAI(api_key=api_key)
    self.model = "gpt-4o-mini"  # "gpt-4o-mini" o "gpt-3.5-turbo"

  def send_message(self, message, frustration):
    print(f"Usando OpenAIService con modello {self.model}")
    system_instruction = get_system_prompt(frustration)
    response = self.client.chat.completions.create(
      model=self.model,
      max_tokens=100,
      temperature=0.8,
      messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": message}
      ], 
    )
    ai_msg = response.choices[0].message.content

    return ai_msg