
import logging
import json
from typing import Dict, Any
from utils.llm_utils import LLMUtils
from config.settings import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeContentAgent:
    def __init__(self):
        self.llm_utils = LLMUtils(provider="google", model_name=Config.GEMINI_MODEL)

    def generate_video_content(self, topic: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"Generating YouTube video content for topic: {topic}")
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
            human_prompt += "\n\n**CRITICAL: Return ONLY a valid JSON object with 'full_script' and 'brief_script' keys. Do not include any explanatory text or markdown outside the JSON structure. Ensure the response is parseable as JSON without additional processing.**\n**IMPORTANT: All double quotes within the 'full_script' and 'brief_script' content MUST be escaped (e.g., \" becomes \\\").**"
            response_str = self.llm_utils.invoke(system_prompt, human_prompt)
            print("Raw response:", response_str)
            try:
                import re
                # Attempt to extract JSON from response if it's wrapped in markdown code blocks
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_str)
                if json_match:
                    json_string = json_match.group(1)
                else:
                    json_match = re.search(r'```\s*([\s\S]*?)\s*```', response_str)
                    if json_match:
                        json_string = json_match.group(1)
                    else:
                        # If no markdown block, assume the entire response is the JSON string
                        json_string = response_str.strip()

                # Pre-process to escape unescaped double quotes within script content
                # This is a targeted replacement for content within "full_script" and "brief_script" values
                def escape_quotes_in_scripts(match):
                    key = match.group(1)
                    value = match.group(2)
                    # Escape only unescaped double quotes within the value
                    escaped_value = re.sub(r'(?<!\\)"', r'\\"', value)
                    return f'"{key}": "{escaped_value}"'

                # Apply the escaping only to the script content, not the JSON structure itself
                json_string = re.sub(r'"(full_script|brief_script)":\s*"(.*?)(?<!\\)"', escape_quotes_in_scripts, json_string, flags=re.DOTALL)
                print("Repaired JSON string for parsing:", json_string[:1000] + "..." if len(json_string) > 1000 else json_string)

                video_content = json.loads(json_string)
                if not isinstance(video_content, dict) or 'full_script' not in video_content or 'brief_script' not in video_content:
                    logging.warning("Failed to parse valid JSON for video content. Returning default structure.")
                    video_content = {
                        "full_script": "Failed to generate full script due to parsing error.",
                        "brief_script": "Failed to generate brief script due to parsing error."
                    }
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing failed: {e}. Repaired JSON string: {json_string[:1000] + '...' if len(json_string) > 1000 else json_string}. Raw response: {response_str[:1000] + '...' if len(response_str) > 1000 else response_str}. Returning default structure.")
                video_content = {
                    "full_script": "Failed to generate full script due to parsing error.",
                    "brief_script": "Failed to generate brief script due to parsing error."
                }
            except Exception as e:
                logging.error(f"An unexpected error occurred during content generation: {e}. Returning default structure.")
                video_content = {
                    "full_script": "Error generating full script.",
                    "brief_script": "Error generating brief script."
                }
            logging.info("Successfully generated YouTube video content.")
            return video_content
        except Exception as e:
            logging.error(f"Error generating YouTube video content: {e}")
            return {"full_script": "Error generating full script.", "brief_script": "Error generating brief script."}
