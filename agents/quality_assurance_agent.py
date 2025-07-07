
from utils.llm_utils import LLMUtils
from config.settings import Config
from typing import Dict, Any
import json

class QualityAssuranceAgent:
    def __init__(self):
        self.llm_utils = LLMUtils(provider="openrouter", model_name=Config.DEEPSEEK_MODEL, temperature=0.2)
    
    def evaluate_content(self, content_package: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive quality evaluation for overall package"""
        system_prompt = '''
        You are a comprehensive quality assurance agent for YouTube content packages.
        
        Evaluation Criteria (1-10 scale):
        1. Technical Accuracy (25%)
        2. Educational Value (25%) 
        3. Engagement Factor (20%)
        4. Content Structure (15%)
        5. SEO Optimization (15%)
        
        Additional Checks:
        - Title clickability
        - Description SEO
        - Hashtag relevance
        - Content comprehensiveness
        - Audience appeal
        
        Return JSON format:
        {
            "technical_accuracy": float_score,
            "educational_value": float_score,
            "engagement_factor": float_score,
            "content_structure": float_score,
            "seo_optimization": float_score,
            "overall_score": float_calculated_score,
            "feedback": "Detailed feedback for improvement",
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"]
        }
        All scores should be floats between 0.0 and 10.0.
        '''
        
        human_prompt = f'''
        EVALUATE THIS CONTENT PACKAGE:
        
        {json.dumps(content_package, indent=2)}
        
        Provide detailed scoring and actionable feedback.
        '''
        
        raw_content = self.llm_utils.invoke(system_prompt, human_prompt)
        result = self.llm_utils._parse_and_repair_json(raw_content)
        return result
        
        # Calculate overall score if not provided
        if 'overall_score' not in result:
            result['overall_score'] = (
                result.get('technical_accuracy', 0) * 0.25 +
                result.get('educational_value', 0) * 0.25 +
                result.get('engagement_factor', 0) * 0.20 +
                result.get('content_structure', 0) * 0.15 +
                result.get('seo_optimization', 0) * 0.15
            )
        
        return result
