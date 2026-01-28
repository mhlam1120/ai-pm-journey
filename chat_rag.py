import os
import sys
from dotenv import load_dotenv

# --- IMPORTS ---
# We ONLY use the parts that are working: The Database and The AI Model.
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
# ----------------

# 1. SETUP
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# 2. LOAD THE BRAIN
print("--- 🧠 Waking up the Vector Database... ---")
try:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004")
    vector_db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
except Exception as e:
    print(f"❌ Critical Error loading database: {e}")
    print("Did you run build_db.py first?")
    sys.exit()

# 3. SETUP THE AI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0
)

print("--- ✅ Manual RAG System Online (Type 'quit' to exit) ---")

# 4. THE CHAT LOOP (Manual Logic)
while True:
    query = input("\nAsk your Data: ").strip()

    if query.lower() in ["quit", "exit", "done"]:
        break
    if not query:
        continue

    print("   🔍 Searching database...")

    try:
        # STEP A: Search the DB manually
        # k=3 means "Give me the top 3 best matching paragraphs"
        results = vector_db.similarity_search(query, k=3)

        if not results:
            print("   ⚠️ No relevant info found in documents.")
            continue

        # STEP B: Combine the found text into one big string (The Context)
        context_text = "\n\n".join([doc.page_content for doc in results])

        # STEP C: Build the Prompt Manually
        # This is exactly what 'RetrievalQA' was doing behind the scenes!
        prompt = f"""
        You are a helpful assistant. Answer the user's question based ONLY on the context below.
        If the answer is not in the context, say "I don't know."

        CONTEXT:
        {context_text}

        QUESTION:
        {query}
        """

        # STEP D: Send to AI
        response = llm.invoke(prompt)

        print(f"\n🤖 ANSWER:\n{response.content}")

        # Optional: Show sources
        print("\n📄 SOURCES:")
        for doc in results:
            source = doc.metadata.get('source', 'Unknown').split('/')[-1]
            print(f" - {source}")

    except Exception as e:
        print(f"❌ Error: {e}")
