from google import genai

# Using your verified key
GOOGLE_API_KEY = "PASTE_YOUR_KEY_HERE"

client = genai.Client(api_key=GOOGLE_API_KEY)

print("--- Sending request to Gemini... ---")

try:
    # Switching to the 'Latest' alias which is usually most stable for free tier
    response = client.models.generate_content(
        model="gemini-flash-latest", 
        contents="Explain what a Product Manager does in one sentence."
    )
    print(f"\n🎉 SUCCESS! AI Response:\n{response.text}")
except Exception as e:
    print(f"\n❌ Error: {e}")