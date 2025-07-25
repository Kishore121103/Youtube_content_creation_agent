
import logging
from utils.llm_utils import LLMUtils
from config.settings import Config
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TitleGeneratorAgent:
    def __init__(self):
        self.llm_utils = LLMUtils(provider="openrouter", model_name=Config.DEEPSEEK_MODEL, temperature=0.8)
        logging.info("TitleGeneratorAgent initialized.")
    
    def generate_titles(self, topic: str, research_data: Dict[str, Any]) -> List[str]:
        logging.info(f"TitleGeneratorAgent: Generating titles for topic: {topic}")
        logging.debug(f"TitleGeneratorAgent: Research data for titles: {research_data}")
        """Generate 5 compelling titles for the video"""
        system_prompt = f'''
        You are a YouTube title optimization expert for the tech channel {Config.CHANNEL_NAME}.
        
        Title Requirements:
        1. Click-worthy but not clickbait
        2. Include relevant keywords
        3. Appeal to different skill levels
        4. Use power words and emotional triggers
        5. 60 characters or less for optimal display
        6. Include numbers, questions, or brackets when appropriate
        
        Generate titles that would attract:
        - Beginners looking to learn
        - Intermediate developers seeking best practices
        - Advanced users wanting expert insights
        
        Return exactly 5 titles in JSON format: {{"titles": ["title1", "title2", ...]}}
        '''
        
        human_prompt = f'''
        TOPIC: {topic}
        
        RESEARCH CONTEXT:
        Technical Details: {research_data.get('technical_details', 'N/A')}
        Difficulty Level: {research_data.get('difficulty_analysis', 'N/A')}
        Industry Relevance: {research_data.get('industry_relevance', 'N/A')}
        
        Create 5 engaging titles that would make viewers want to click and learn.
        '''
        
        logging.debug("TitleGeneratorAgent: Invoking LLM for title generation.")
        raw_content = self.llm_utils.invoke(system_prompt, human_prompt)
        logging.debug(f"TitleGeneratorAgent: Raw LLM response: {raw_content}")
        
        result = self.llm_utils._parse_and_repair_json(raw_content)
        logging.info("TitleGeneratorAgent: Titles generated.")
        logging.debug(f"TitleGeneratorAgent: Parsed titles: {result.get('titles', [])}")
        return result.get('titles', [])
