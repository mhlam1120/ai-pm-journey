from google import genai

# REPLACE WITH YOUR KEY
GOOGLE_API_KEY = "AIzaSyBim_oY84gRiVdu-6FV97aFMANofLjFeXk"

client = genai.Client(api_key=GOOGLE_API_KEY)

print("--- Fetching available models... ---")

try:
    # 1. List all models
    for model in client.models.list():
        # 2. In the NEW library, we check 'supported_actions' not 'supported_generation_methods'
        if model.supported_actions and "generateContent" in model.supported_actions:
            print(f"Model Name: {model.name}")
            print(f"Display Name: {model.display_name}")
            print("-" * 20)
except Exception as e:
    print(f"An error occurred: {e}")
    # Troubleshooting helper: prints all attributes if the above fails
    # print(dir(model))