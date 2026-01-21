import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. SETUP
# ---------------------------------------------------------
# Load environment variables from the .env file
load_dotenv()

# Fetch the key from the secret file
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found! Make sure you created the .env file.")

client = genai.Client(api_key=API_KEY)

# 2. THE PERSONA (System Instruction)
# ---------------------------------------------------------
# This is the "Brain" of your product. It tells the AI HOW to behave.
sys_instruct = """
You are an elite Career Coach for Tech Product Managers.
Your goal is to help the user get a $200k+ AI PM role.
You are critical, direct, and focused on 'metrics', 'strategy', and 'technical depth'.
Do not be polite. Be effective.
"""

# 3. THE INTERACTION
# ---------------------------------------------------------
print("--- AI Career Coach Initialized ---")
user_question = input("Ask your coach a question: ")

try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct,
            temperature=0.7 # Creativity level (0.0 = Robot, 1.0 = Poet)
        ),
        contents=user_question
    )
    
    print("\n>>> COACH SAYS:")
    print(response.text)
    
except Exception as e:
    print(f"\n❌ Error: {e}")