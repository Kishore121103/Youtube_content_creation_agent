
import logging
from utils.llm_utils import LLMUtils
from utils.database_manager import DatabaseManager
from config.settings import Config
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ResearchAgent:
    def __init__(self):
        self.llm_utils = LLMUtils(provider="openrouter", model_name=Config.DEEPSEEK_MODEL, temperature=0.3)
        self.db_manager = DatabaseManager()
        logging.info("ResearchAgent initialized.")
    
    def conduct_research(self, topic: str) -> Dict[str, Any]:
        logging.info(f"ResearchAgent: Starting research for topic: {topic}")
        """Conduct comprehensive research on the given topic"""
        system_prompt = f'''
        You are a specialized research agent for programming and tech content creation.
        Your task is to research comprehensive information about the given topic.
        
        Focus Areas: {', '.join(Config.FOCUS_AREAS)}
        Channel: {Config.CHANNEL_NAME}
        
        Research Requirements:
        1. Technical accuracy and depth
        2. Current best practices and trends
        3. Common problems and solutions
        4. Practical applications
        5. Difficulty levels for different audiences
        6. Related concepts and prerequisites
        7. Common misconceptions
        8. Industry use cases
        
        Return your research in JSON format with these keys:
        - "technical_details": Comprehensive technical information
        - "best_practices": Current industry best practices
        - "common_issues": Problems learners face
        - "practical_examples": Real-world applications
        - "difficulty_analysis": Complexity breakdown
        - "prerequisites": Required knowledge
        - "related_topics": Connected concepts
        - "misconceptions": Common wrong assumptions
        - "industry_relevance": How it's used professionally
        - "learning_path": Suggested learning progression
        '''
        
        human_prompt = f'''
        RESEARCH TOPIC: {topic}
        
        Provide comprehensive research that will help create high-quality educational content.
        Make sure to cover both theoretical concepts and practical implementations.
        Include specific examples, code patterns, and real-world scenarios.
        '''
        
        logging.debug("ResearchAgent: Invoking LLM for research.")
        raw_content = self.llm_utils.invoke(system_prompt, human_prompt)
        logging.debug(f"ResearchAgent: Raw LLM response: {raw_content}")
        
        research_data = self.llm_utils._parse_and_repair_json(raw_content)
        logging.info("ResearchAgent: Research complete.")
        logging.debug(f"ResearchAgent: Parsed research data: {research_data}")
        return research_data
