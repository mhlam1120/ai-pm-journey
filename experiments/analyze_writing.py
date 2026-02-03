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
    with open("writing.txt", "r") as r_file:
        writing_content = r_file.read()

   # with open("job_description.txt", "r") as j_file:
   #     jd_content = j_file.read()

except FileNotFoundError:
    print("❌ Error: Make sure you have 'writing.txt'")
    exit()

# 3. THE "FEW-SHOT" PROMPT (Advanced Strategy)
# We are now giving the AI specific context on the TARGET.
prompt = f"""
Act as an Editorial Panel consisting of a Developmental Editor, a Line Editor, and a Proofreader.

WRITING:
{writing_content}

TASK: Perform a "Full-Spectrum Editorial Audit." Act as a Senior Editor, Stylist, and Lead Proofreader simultaneously. 
Analyze the provided text across four distinct layers: Narrative Architecture, Prose Craft, Technical Accuracy, and Reader Experience.

OUTPUT FORMAT:

1. THE BONES (Developmental)

* Narrative Goal: What is the primary purpose of this section?

* Stakes & Logic: Identify any "plot holes" or moments where character behavior feels inconsistent.

* Pacing Score: (Slow / Steady / Fast) with a brief explanation of why.

2. THE MUSCLE (Line Editing)

* Filter Word Audit: List the "crutch words" the author uses too often (e.g., saw, felt, realized, just).

* Dialogue Check: Identify any dialogue that feels stilted, "on-the-nose," or repetitive.

* Voice Consistency: Note any shifts where the narrator’s "voice" suddenly changes or feels out of character.

3. THE SKIN (Proofreading)

* The Error Log: List the top 3-5 recurring grammatical or punctuation errors found.

* Internal Consistency: Flag any contradictions (e.g., a character holding a glass in one sentence and then clapping their hands in the next).

4. THE VERDICT (Reader/Reviewer)

* The "Hook" Rating: (0-10) How effectively does this section compel the reader to continue?

* Emotional Impact: What is the "takeaway" feeling of this passage?

* The "Kill Your Darlings" Suggestion: What is the one sentence or paragraph that could be cut to make the piece stronger?
"""

print("--- Reading and Generating Feedback ---")

try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    print(f"\n{response.text}")

except Exception as e:
    print(f"Error: {e}")
