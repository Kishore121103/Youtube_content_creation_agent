
import logging
import json
from typing import Dict, Any
from utils.llm_utils import LLMUtils
from config.settings import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeContentAgent:
    def __init__(self):
        self.llm_utils = LLMUtils(provider="openrouter", model_name=Config.DEEPSEEK_MODEL, temperature=0.8)
        logging.info("YouTubeContentAgent initialized.")

    def generate_video_content(self, topic: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"YouTubeContentAgent: Generating YouTube video content for topic: {topic}")
        logging.debug(f"YouTubeContentAgent: Research data for video content: {research_data}")
        try:
            system_prompt = "You are a specialized agent for creating engaging and educational YouTube video scripts."
            human_prompt = f"""
            **Objective:** Create detailed and engaging YouTube video scripts for the topic of "{topic}".

            **Context & Tone:** The tone should be conversational, educational, and engaging. The scripts should cater to an audience of intermediate developers. Provide two versions: a full script for a long video and a brief script for a shorter format.

            **Research Data for Context:**
            ```json
            {json.dumps(research_data, indent=2)}
            ```

            **Instructions for Full Script:**
            1. Start with a captivating hook to grab attention.
            2. Introduce the topic and its importance.
            3. Cover key concepts with detailed explanations.
            4. Include practical examples or code snippets.
            5. End with a summary and call to action.

            **Instructions for Brief Script:**
            1. Start with a quick hook.
            2. Briefly introduce the topic.
            3. Highlight the main points or key takeaways.
            4. End with a concise call to action.

            **Output Format:** Return a JSON object with 'full_script' and 'brief_script' keys.

            **Example Output:**
            {{
                "full_script": "Hey everyone, today we're diving into {topic}! Ever wondered how to solve X? Well, {topic} is your answer. Let's break it down step by step. First, we'll cover Y, then dive into Z with some real-world code examples. By the end, you'll be able to implement {topic} in your projects. Stick around and let's get started! ... [detailed content] ... Thanks for watching, smash that like button and subscribe for more!",
                "brief_script": "Hey everyone, quick dive into {topic} today! It's key for solving X. Here's the gist: focus on Y and Z. Check out this quick example. Got it? Great! Like, subscribe, and stay tuned for more!"
            }}

            **Generate the scripts now.**
            """
            # Explicitly instruct the LLM to return strict JSON format to avoid parsing issues
            human_prompt += "\n\n**CRITICAL: Return ONLY a valid JSON object with 'full_script' and 'brief_script' keys. Do not include any explanatory text or markdown outside the JSON structure. Ensure the response is parseable as JSON without additional processing.**\n**IMPORTANT: All double quotes within the 'full_script' and 'brief_script' content MUST be escaped (e.g., \" becomes \\\" ).**"
            logging.debug("YouTubeContentAgent: Invoking LLM for video content generation.")
            video_content = self.llm_utils.invoke(system_prompt, human_prompt, parse_json=True)
            logging.debug(f"YouTubeContentAgent: Parsed video content: {video_content}")

            if not isinstance(video_content, dict) or 'full_script' not in video_content or 'brief_script' not in video_content:
                logging.warning("YouTubeContentAgent: Failed to parse valid JSON for video content. Returning default structure.")
                video_content = {
                    "full_script": "Failed to generate full script due to parsing error.",
                    "brief_script": "Failed to generate brief script due to parsing error."
                }
            logging.info("YouTubeContentAgent: Successfully generated YouTube video content.")
            return video_content
        except Exception as e:
            logging.error(f"YouTubeContentAgent: Error generating YouTube video content: {e}")
            return {"full_script": "Error generating full script.", "brief_script": "Error generating brief script."}
