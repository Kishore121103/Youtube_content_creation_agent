from config.settings import Config # Import Config here

import logging
from logging import StreamHandler # Import StreamHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from langchain_xai import ChatXAI

import json
import re
from openai import OpenAI  # Import OpenAI client for OpenRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genkodex.log'), # Changed to genkodex.log
        StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LLMUtils:
    def __init__(self, provider: str = None, model_name: str = None, temperature: float = None, max_tokens: int = None):
        self.provider = provider or Config.LLM_PROVIDER
        self.provider = provider or Config.LLM_PROVIDER
        self.model_name = model_name or Config.MODEL_NAME
        self.temperature = temperature if temperature is not None else Config.TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else Config.MAX_TOKENS
        logger.info(f"Initializing LLM: provider={self.provider}, model={self.model_name}, temperature={self.temperature}, max_tokens={self.max_tokens}")
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the LLM based on the provider."""
        try:
            if self.provider.lower() == "google":
                if not Config.GOOGLE_API_KEY:
                    logger.error("GOOGLE_API_KEY is not set in .env")
                    raise ValueError("GOOGLE_API_KEY is not set in .env")
                logger.debug("Initializing ChatGoogleGenerativeAI")
                return ChatGoogleGenerativeAI(
                    google_api_key=Config.GOOGLE_API_KEY,
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

            elif self.provider.lower() == "grok":
                if not Config.GROK_API_KEY:
                    logger.error("GROK_API_KEY is not set in .env")
                    raise ValueError("GROK_API_KEY is not set in .env")
                logger.debug("Initializing ChatGrok")
                return ChatXAI(
                    api_key=Config.GROK_API_KEY,
                    model=Config.GROK_MODEL,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

            elif self.provider.lower() == "openrouter":
                if not Config.OPENROUTER_API_KEY:
                    logger.error("OPENROUTER_API_KEY is not set in .env")
                    raise ValueError("OPENROUTER_API_KEY is not set in .env")
                logger.debug("Initializing OpenRouter client for DeepSeek")
                # Initialize OpenAI client with OpenRouter's endpoint
                client = OpenAI(
                    api_key=Config.OPENROUTER_API_KEY,
                    base_url="https://openrouter.ai/api/v1"
                )
                return client

            else:
                logger.error(f"Unsupported LLM provider: {self.provider}")
                raise ValueError(f"Unsupported LLM provider: {self.provider}")

        except Exception as e:
            logger.exception(f"Failed to initialize LLM: {str(e)}")
            raise RuntimeError(f"Failed to initialize LLM: {str(e)}")

    def invoke(self, system_prompt: str, human_prompt: str, parse_json: bool = False):
        """Invoke the LLM with system and human prompts."""
        try:
            logger.debug(f"System prompt: {system_prompt[:500]}...")
            logger.debug(f"Human prompt: {human_prompt[:500]}...")
            
            if self.provider.lower() == "openrouter":
                # Handle OpenRouter invocation
                client = self.llm
                response = client.chat.completions.create(
                    model=Config.DEEPSEEK_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": human_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                content = response.choices[0].message.content
            else:
                # Existing logic for Google and Grok
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt)
                ]
                logger.info("Invoking LLM")
                response = self.llm.invoke(messages)
                content = response.content

            logger.debug(f"Raw LLM response: {content[:1000]}...")
            
            if parse_json:
                logger.info("Attempting to parse response as JSON")
                return self._parse_and_repair_json(content)
            
            logger.info("Returning raw response content")
            return content
            
        except Exception as e:
            logger.exception(f"LLM invocation failed: {str(e)}")
            raise RuntimeError(f"LLM invocation failed: {str(e)}")

    def _parse_and_repair_json(self, raw_json_string: str) -> dict:
        """
        Parses a raw string that is expected to be a JSON object.
        Attempts to repair common LLM output issues like markdown code blocks.
        """
        # Remove markdown code block fences if present
        cleaned_string = raw_json_string.strip()
        if cleaned_string.startswith("```json") and cleaned_string.endswith("```"):
            cleaned_string = cleaned_string[7:-3].strip()
        elif cleaned_string.startswith("```") and cleaned_string.endswith("```"):
            cleaned_string = cleaned_string[3:-3].strip()

        try:
            return json.loads(cleaned_string)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON decode failed: {e}. Attempting repair...")
            # Attempt to find the first and last curly braces to extract the JSON
            match = re.search(r'\{.*\}', cleaned_string, re.DOTALL)
            if match:
                try:
                    extracted_json_str = match.group(0)
                    return json.loads(extracted_json_str)
                except json.JSONDecodeError as e_inner:
                    logger.error(f"Failed to parse extracted JSON: {e_inner}")
                    raise ValueError(f"Could not parse or repair JSON: {raw_json_string}") from e_inner
            else:
                logger.error("No JSON object found in the string.")
                raise ValueError(f"No JSON object found in the string: {raw_json_string}") from e