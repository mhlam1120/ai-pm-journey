import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. SETUP
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

# 2. GET USER INPUT
user_input = input(
    "Tell your coach how you are feeling about your job search: ")

print("\n--- 🧠 Tier 1: The Gatekeeper ---")

# 3. TIER 1: BROAD CLASSIFICATION
# We first determine the general direction (Positive/Negative/Ambiguous)
tier1_prompt = f"""
Analyze this text: "{user_input}"
Classify it into exactly ONE of these 3 buckets:
1. POSITIVE (Happy, Excited, Proud)
2. NEGATIVE (Sad, Angry, Scared, Tired)
3. AMBIGUOUS (Curious, Confused, Unsure, Neutral)

Output JUST the word: POSITIVE, NEGATIVE, or AMBIGUOUS.
"""

response_t1 = client.models.generate_content(
    model="gemini-flash-latest",
    contents=tier1_prompt
)
bucket = response_t1.text.strip().upper()
print(f"Detected Bucket: {bucket}")

# 4. TIER 2: THE SPECIALIST (Nested Logic)
persona = ""

if "NEGATIVE" in bucket:
    print("--- 📉 Tier 2: Diagnosing Negative Emotion... ---")
    # Sub-classification for Negative
    tier2_prompt = f"""
    The user is feeling negative. Analyze specifically WHICH negative emotion: "{user_input}"
    Classify as exactly ONE word:
    - FRUSTRATED (Angry, Annoyed, Blocked) -> Needs a Solution.
    - ANXIOUS (Scared, Nervous, Worried) -> Needs Reassurance/Calm.
    - DEFEATED (Sad, Hopeless, Resigned) -> Needs Hope.
    
    Output JUST the word.
    """
    response_t2 = client.models.generate_content(
        model="gemini-flash-latest", contents=tier2_prompt)
    sub_mood = response_t2.text.strip().upper()
    print(f"Specific Diagnosis: {sub_mood}")

    if "FRUSTRATED" in sub_mood:
        persona = "You are a pragmatic problem-solver. The user is annoyed. Give them a direct, 3-step technical solution."
    elif "ANXIOUS" in sub_mood:
        persona = "You are a grounding presence. The user is scared. Validate their fear, then give them one small, safe step to take."
    else:  # Defeated
        persona = "You are a warm, supportive mentor. The user has lost hope. Remind them of their value and offer encouragement."

elif "AMBIGUOUS" in bucket:
    # Your "Socratic" Decision
    persona = "You are a Socratic Career Coach. The user is unsure or curious. Do NOT give the answer. Instead, ask a guiding question to help them find the answer themselves."

else:  # Positive
    persona = "You are a high-energy hype man! The user is winning. Celebrate with them! 🎉"

# 5. THE COACH RESPONDS
print(f"\n--- 🤖 Agent Responding... ---")
response = client.models.generate_content(
    model="gemini-flash-latest",
    config=types.GenerateContentConfig(system_instruction=persona),
    contents=user_input
)

print(f"\n>>> COACH SAYS:\n{response.text}")
