import os
from dotenv import load_dotenv
from google import genai

# 1. SETUP
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

# 2. LOAD DATA (Now reading TWO sources)
print("--- Reading files... ---")

try:
    with open("resume.txt", "r") as r_file:
        resume_content = r_file.read()

    with open("job_description.txt", "r") as j_file:
        jd_content = j_file.read()

except FileNotFoundError:
    print("❌ Error: Make sure you have both 'resume.txt' and 'job_description.txt'")
    exit()

# 3. THE "FEW-SHOT" PROMPT (Advanced Strategy)
# We are now giving the AI specific context on the TARGET.
prompt = f"""
ou are a ruthless, cynical Career Coach who only cares about hard metrics and ignores fluff.

JOB DESCRIPTION:
{jd_content}

RESUME:
{resume_content}

TASK:
Perform a "Gap Analysis". Compare the resume strictly against the JD requirements.

OUTPUT FORMAT:
1. **Match Score:** (0-100%)
2. **Missing Keywords:** List technical terms present in the JD but missing from the Resume.
3. **Critical Feedback:** Explain why this candidate would or would not get an interview.
"""

print("--- Comparing Resume to JD... ---")

try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    print(f"\n{response.text}")

except Exception as e:
    print(f"Error: {e}")
