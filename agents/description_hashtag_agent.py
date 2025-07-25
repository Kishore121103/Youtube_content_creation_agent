
import logging
from utils.llm_utils import LLMUtils
from config.settings import Config
from typing import Dict, Any
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DescriptionHashtagAgent:
    def __init__(self):
        self.llm_utils = LLMUtils(provider="openrouter", model_name=Config.DEEPSEEK_MODEL, temperature=0.6)
        logging.info("DescriptionHashtagAgent initialized.")
    
    def generate_description_and_hashtags(self, topic: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"DescriptionHashtagAgent: Generating description and hashtags for topic: {topic}")
        logging.debug(f"DescriptionHashtagAgent: Research data for description/hashtags: {research_data}")
        description = self.generate_description(topic, research_data)
        hashtags = self.generate_hashtags(topic, research_data)
        logging.info("DescriptionHashtagAgent: Description and hashtags generation complete.")
        return {"description": description, "hashtags": hashtags}

    def generate_description(self, topic, research_data):
        logging.info(f"DescriptionHashtagAgent: Generating description for topic: {topic}")
        """
        Generates a concise and SEO-friendly description for the content.
        """
        prompt = f"""
        **Objective:** Create a compelling and SEO-optimized description for educational content about "{topic}".

        **Context:**
        The description will be used for social media, video platforms, and blog posts. It needs to be engaging, informative, and contain relevant keywords to improve visibility. Use the provided research data to inform the description.

        **Research Data:**
        ```json
        {json.dumps(research_data, indent=2)}
        ```

        **Instructions:**
        1.  Start with a hook that clearly states what the content is about and its main benefit.
        2.  Briefly summarize the key concepts that will be covered.
        3.  Incorporate important keywords naturally.
        4.  Keep the description concise, ideally between 100-150 words.
        5.  The output should be a single block of text.

        **Example Output:**
        "Dive deep into {topic} and learn how to write highly efficient, non-blocking code. In this comprehensive guide, we'll cover everything from the basics of asynchronous programming to advanced patterns like `async/await` and structured concurrency. Perfect for developers looking to level up their skills and build faster, more scalable applications. #Python #Async #Programming #Developer"

        **Generate the description now.**
        """
        system_prompt = "You are a specialized agent for generating SEO-optimized content descriptions."
        description_content = self.llm_utils.invoke(system_prompt, prompt)
        logging.info("DescriptionHashtagAgent: Description generated.")
        return description_content

    def generate_hashtags(self, topic, research_data):
        logging.info(f"DescriptionHashtagAgent: Generating hashtags for topic: {topic}")
        """
        Generates a list of relevant hashtags for the content.
        """
        prompt = f"""
        **Objective:** Generate a list of relevant and trending hashtags for content about "{topic}".

        **Context:**
        Hashtags are crucial for discoverability on social media and video platforms. They should be a mix of broad, niche, and specific tags related to the topic.

        **Research Data:**
        ```json
        {json.dumps(research_data, indent=2)}
        ```

        **Instructions:**
        1.  Identify the core concepts and technologies related to "{topic}".
        2.  Include a mix of popular hashtags (e.g., #programming, #developer) and more specific ones (e.g., #{topic.replace(' ', '')}, #asyncio).
        3.  Consider related fields and applications.
        4.  Provide a list of 10-15 hashtags.
        5.  The output should be a JSON array of strings.

        **Example Output:**
        ```json
        [
            "python",
            "async",
            "await",
            "asynchronous",
            "programming",
            "developer",
            "softwareengineering",
            "coding",
            "webdevelopment",
            "concurrency"
        ]
        ```

        **Generate the JSON array of hashtags now.**
        """
        system_prompt = "You are a specialized agent for generating relevant hashtags for content."
        response_str = self.llm_utils.invoke(system_prompt, prompt)
        logging.debug(f"DescriptionHashtagAgent: Raw LLM response for hashtags: {response_str}")
        try:
            # Clean the response to ensure it's a valid JSON string
            start_index = response_str.find('[')
            end_index = response_str.rfind(']') + 1
            if start_index != -1 and end_index != -1:
                json_str = response_str[start_index:end_index]
                hashtags = json.loads(json_str)
                logging.info("DescriptionHashtagAgent: Successfully parsed hashtags JSON.")
                return hashtags
            else:
                logging.warning("DescriptionHashtagAgent: No JSON array found in the response for hashtags. Attempting fallback.")
                # Fallback for plain text list
                return [tag.strip().replace('#', '') for tag in response_str.split()]
        except json.JSONDecodeError as e:
            logging.error(f"DescriptionHashtagAgent: JSON decoding error for hashtags: {e}. Attempting fallback.")
            # Fallback for plain text list
            return [tag.strip().replace('#', '') for tag in response_str.split()]
