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
        Attempts to repair common LLM output issues like markdown code blocks, unescaped quotes, and incomplete JSON.
        """
        cleaned_string = raw_json_string.strip()

        # 1. Attempt to extract JSON from markdown code blocks
        match_json_block = re.search(r'```json\s*([\s\S]*?)\s*```', cleaned_string)
        match_generic_block = re.search(r'```\s*([\s\S]*?)\s*```', cleaned_string)

        if match_json_block:
            json_str = match_json_block.group(1).strip()
        elif match_generic_block:
            json_str = match_generic_block.group(1).strip()
        else:
            json_str = cleaned_string

        # 2. Attempt to parse directly
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON decode failed: {e}. Attempting repair...")

            # 3. Try to repair common issues (e.g., unescaped quotes, trailing commas, comments)
            # This is a basic attempt; for more complex cases, a dedicated JSON repair library might be needed.
            repaired_json_str = json_str
            # Remove trailing commas (simple cases)
            repaired_json_str = re.sub(r',\s*([}\]])', r'\1', repaired_json_str)
            # Replace single quotes with double quotes for keys and string values
            repaired_json_str = re.sub(r"'([a-zA-Z0-9_]+)':", r'"\1":', repaired_json_str) # for keys
            repaired_json_str = re.sub(r":\s*'(.*?)'", r': "\1"', repaired_json_str) # for values
            
            
            # Escape unescaped double quotes within string values
            # Escape unescaped double quotes within string values more carefully
            # This is a complex problem, and a simple regex might not cover all edge cases.
            # A common issue is when the LLM generates JSON with unescaped quotes inside string values.
    def _generate_main_title_section(self, topic: str) -> dict:
        """Generate main title section for PDF"""
        return {
            "type": "heading",
            "text": f"Educational Content: {topic}",
            "style": {
                "font_size": 24,
                "text_color": "#2E8B57",
                "alignment": "center",
                "space_after": 30
            }
        }

    def _generate_introduction_section(self, content_intro: str) -> dict:
        """Generate introduction section for PDF"""
        return {
            "type": "section_heading",
            "text": "Introduction",
            "style": {
                "font_size": 18,
                "text_color": "#36454F",
                "alignment": "left",
                "space_after": 10
            }
        }

    def _generate_approach_section(self, approach: dict, approach_num: int) -> dict:
        """Generate approach section for PDF"""
        content_items = []
        
        # Add explanation
        if approach.get('explanation'):
            content_items.append({
                "type": "paragraph",
                "text": approach['explanation'],
                "style": {"font_size": 11, "space_after": 10}
            })
        
        # Add code examples
        if approach.get('code_examples'):
            content_items.append({
                "type": "sub_heading",
                "text": "Code Examples:",
                "style": {"font_size": 12, "text_color": "#4169E1", "space_after": 5}
            })
            for code in approach['code_examples']:
                content_items.append({
                    "type": "code_block",
                    "text": code,
                    "style": {
                        "font_size": 9,
                        "background_color": "#F5F5F5",
                        "padding": 5,
                        "space_after": 10
                    }
                })
        
        return {
            "type": "approach",
            "title": approach.get('title', f'Approach {approach_num}'),
            "content": content_items,
            "style": {
                "title_font_size": 14,
                "title_text_color": "#2E8B57",
                "box_background_color": "#F8F8FF",
                "box_border_color": "#D3D3D3",
                "padding": 15,
                "space_after": 20
            }
        }

    def _generate_research_data_section(self, research_data: dict) -> dict:
        """Generate research data section for PDF"""
        content = []
        content.append({
            "type": "section_heading",
            "text": "Research Data",
            "style": {"font_size": 18, "text_color": "#36454F", "space_after": 15}
        })
        
        key_value_data = []
        for key, value in research_data.items():
            if isinstance(value, (str, int, float)):
                key_value_data.append({
                    "key": key.replace('_', ' ').title(),
                    "value": str(value)[:200] + "..." if len(str(value)) > 200 else str(value),
                    "style": {"font_size": 10, "key_color": "#4169E1", "space_after": 8}
                })
        
        if key_value_data:
            content.append({
                "type": "key_value_list",
                "data": key_value_data
            })
        
        return {"content": content}

    def _generate_metadata_section(self, titles: list, description: str, hashtags: list) -> dict:
        """Generate metadata section for PDF"""
        content = []
        content.append({
            "type": "section_heading",
            "text": "Content Metadata",
            "style": {"font_size": 18, "text_color": "#36454F", "space_after": 15}
        })
        
        # Suggested titles
        content.append({
            "type": "list",
            "heading": "Suggested Titles",
            "items": titles,
            "style": {"font_size": 11, "space_after": 15}
        })
        
        # Description
        content.append({
            "type": "sub_heading",
            "text": "Description:",
            "style": {"font_size": 12, "text_color": "#4169E1", "space_after": 5}
        })
        content.append({
            "type": "paragraph",
            "text": description,
            "style": {"font_size": 10, "space_after": 15}
        })
        
        # Hashtags
        content.append({
            "type": "sub_heading",
            "text": "Hashtags:",
            "style": {"font_size": 12, "text_color": "#4169E1", "space_after": 5}
        })
        content.append({
            "type": "paragraph",
            "text": " ".join([f"#{tag}" for tag in hashtags]),
            "style": {"font_size": 10, "space_after": 10}
        })
        
        return {"content": content}
            # We'll try to replace " with \" only if it's not already escaped.
            # This regex looks for a quote that is not preceded by an odd number of backslashes.
            temp_str = []
            i = 0
            while i < len(repaired_json_str):
                if repaired_json_str[i] == '\\' and i + 1 < len(repaired_json_str) and repaired_json_str[i+1] == '"':
                    temp_str.append(repaired_json_str[i]) # Keep the backslash
                    temp_str.append(repaired_json_str[i+1]) # Keep the escaped quote
                    i += 2
                elif repaired_json_str[i] == '"':
                    temp_str.append('\\') # Add escape character
                    temp_str.append(repaired_json_str[i]) # Add the quote
                    i += 1
                else:
                    temp_str.append(repaired_json_str[i])
                    i += 1
            repaired_json_str = "".join(temp_str)