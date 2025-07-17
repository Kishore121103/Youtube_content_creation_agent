
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Configuration
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    GROK_MODEL = os.getenv("GROK_MODEL", "grok-3")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash") # Using a Google model
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 16000))
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model names for different tasks
    FAST_MODEL = os.getenv("FAST_MODEL", "gemini-1.5-flash") # Using a Google model
    SMART_MODEL = os.getenv("SMART_MODEL", "gemini-1.5-pro") # Using a Google model
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL") # A good model for code generation
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash") # Default Gemini model
    
    # Content Generation Settings
    CHANNEL_NAME = "GenKodex"
    FOCUS_AREAS = ["Python", "AI/ML", "Data Science", "Generative AI"]
    TARGET_AUDIENCE = ["Beginners", "Intermediate", "Advanced"]
    
    # Quality Assurance Thresholds
    QUALITY_THRESHOLD = float(os.getenv("QUALITY_THRESHOLD", 7.5)) # Minimum score for content to be approved
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 3)) # Maximum refinement iterations

    # Database Settings
    DATABASE_PATH = os.getenv("DATABASE_PATH", "genkodex_content.db")

    # Ensure at least one API key is loaded
    
