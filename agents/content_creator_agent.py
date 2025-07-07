from utils.llm_utils import LLMUtils
from config.settings import Config
import json

class ContentCreatorAgent:
    def __init__(self):
        self.llm = LLMUtils(provider="google", model_name=Config.GEMINI_MODEL)

    def create_content_introduction(self, topic, research_data):
        """
        Generates a captivating and structured introduction for a YouTube video.
        """
        prompt = f"""
        **Objective:** Create a compelling, conversational, and educational introduction for a YouTube video on the topic of "{topic}".

        **Context & Tone:** The tone should be enthusiastic, engaging, and build curiosity. Assume you are speaking directly to an audience of intermediate developers. The introduction should be a script, not just a paragraph.

        **Research Data for Context:**
        ```json
        {json.dumps(research_data, indent=2)}
        ```

        **Instructions:**
        1.  **Hook:** Start with a strong, relatable question or a surprising statement that grabs the viewer's attention immediately.
        2.  **Problem Statement:** Clearly articulate the problem or challenge that understanding "{topic}" solves.
        3.  **Value Proposition:** Explicitly state what the viewer will learn and be able to do by the end of the video.
        4.  **Outline:** Briefly mention the key concepts or approaches that will be covered.
        5.  **Call to Engagement:** End with a soft call to action, like "Let's dive in!" or "Let's get started!"
        6.  **Output:** The output should be a single, well-written string of text representing the script for the introduction.

        **Example Output Structure:**
        "Ever wondered how to handle thousands of simultaneous requests in your Python application without bringing your server to its knees? That's where the real power of asynchronous programming comes in, and it's a total game-changer. In this video, we're going to unlock the secrets of high-performance Python by diving deep into async/await and event loops. We'll start with the absolute basics and work our way up to pro-level techniques that you can use in your real-world projects. Ready to level up your coding skills? Let's dive in!"

        **Generate the introduction script now.**
        """
        system_prompt = "You are a specialized agent for creating engaging YouTube video introductions."
        return self.llm.invoke(system_prompt, prompt)

    def generate_single_approach(self, topic, research_data, approach_desc):
        """
        Generates a single, detailed approach to explain the topic.
        """
        prompt = f"""
        **Objective:** Develop a single, detailed approach to explain the programming topic: "{topic}". This approach should be tailored to the following pedagogical style: "{approach_desc}". The final output must be a clean, valid JSON object.

        **Context & Pedagogy:** The goal is to create a comprehensive educational unit. This approach should be self-contained and provide a complete explanation of the concept from its unique perspective.

        **Research Data for Context:**
        ```json
        {json.dumps(research_data, indent=2)}
        ```

        **Instructions:**
        1.  **Content per Approach:** The approach object **MUST** contain:
            *   `title`: A descriptive title for the approach (e.g., "The 101 Guide to {topic}", "Level Up: Practical {topic} Patterns", "Pro-Tip: Avoiding a Common {topic} Trap").
            *   `explanation`: A detailed, step-by-step explanation of the concept from this approach's perspective. Use clear, concise language.
            *   `code_examples`: An array of strings, where each string is a complete, runnable, and well-commented code snippet. The code must be functional and directly illustrate the explanation.
        2.  **Code Quality:** All code examples must be:
            *   **Functional:** They must run without errors.
            *   **Relevant:** They must directly demonstrate the point being explained.
            *   **Well-Commented:** The comments should explain the 'why' behind the code, not just the 'what'.
        3.  **Final Output:** The final output **MUST** be a single, valid JSON object and nothing else. Do not include any text before or after the JSON object.

        **Generate the JSON object now.**
        """
        system_prompt = "You are a specialized agent for explaining programming concepts in detail."
        response_str = self.llm.invoke(system_prompt, prompt)
        try:
            # Clean the response to ensure it's a valid JSON string
            start_index = response_str.find('{')
            end_index = response_str.rfind('}') + 1
            if start_index != -1 and end_index != -1:
                json_str = response_str[start_index:end_index]
                result = json.loads(json_str)
                # Check if the result has the expected structure
                if isinstance(result, dict) and 'title' in result and 'explanation' in result and 'code_examples' in result:
                    return result
                else:
                    return {
                        "title": "Error in Content Generation",
                        "explanation": "Failed to generate valid content due to invalid JSON structure.",
                        "code_examples": []
                    }
            else:
                raise json.JSONDecodeError("No JSON object found in the response.", response_str, 0)
        except json.JSONDecodeError:
            return {
                "title": "Error in Content Generation",
                "explanation": "Failed to parse JSON response from content generation.",
                "code_examples": []
            }
