import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

# 1. SETUP
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

# 2. THE INGESTION ENGINE (Multi-File Support)
print("--- 📂 Reading ALL PDFs in folder... ---")

pdf_text = ""
pdf_count = 0

# Loop through files in the current directory
for filename in os.listdir('.'):
    if filename.endswith('.pdf'):
        try:
            reader = PdfReader(filename)
            # Add a header so the AI knows which file the text comes from
            pdf_text += f"\n--- START OF FILE: {filename} ---\n"
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"
            print(f"   ✅ Ingested: {filename}")
            pdf_count += 1
        except Exception as e:
            print(f"   ⚠️ Skipped {filename}: {e}")

if pdf_count == 0:
    print("❌ Error: No PDFs found. Drag a .pdf file into this folder first.")
    exit()

print(f"--- 🧠 Loaded {pdf_count} documents into memory ---")

# 3. THE CHAT LOOP (Now with Better Exit Logic)
system_instruction = f"""
You are an expert analyst. 
Your brain contains ONLY the following documents. 
Answer the user's questions based strictly on this text.
If the answer is not in the text, say "I don't find that in the documents."

DOCUMENTS CONTENT:
{pdf_text}
"""

print("\n--- 🤖 Knowledge Base Ready ---")
print("Type 'quit', 'exit', or 'done' to end the session.\n")

while True:
    try:
        user_question = input("Ask the Documents: ").strip()

        # Check for multiple exit keywords
        if user_question.lower() in ["quit", "exit", "done", "bye"]:
            print("👋 Exiting. Good luck!")
            break

        # Skip empty inputs (hitting enter accidentally)
        if not user_question:
            continue

        response = client.models.generate_content(
            model="gemini-flash-latest",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            ),
            contents=user_question
        )

        print(f"\nAnswer: {response.text}\n")

    except KeyboardInterrupt:
        # Handles Ctrl+C gracefully
        print("\n\n👋 Forced Exit. See you later!")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
