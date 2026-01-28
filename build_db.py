import os
import time
from dotenv import load_dotenv

# --- IMPORTS ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
# -----------------------

# 1. SETUP
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# 2. LOAD PDFS
documents = []
print("--- 📂 Scanning for PDFs... ---")
for filename in os.listdir('.'):
    if filename.endswith('.pdf'):
        try:
            loader = PyPDFLoader(filename)
            docs = loader.load()
            documents.extend(docs)
            print(f"   ✅ Loaded: {filename} ({len(docs)} pages)")
        except Exception as e:
            print(f"   ❌ Failed to load {filename}: {e}")

if not documents:
    print("❌ No PDFs found.")
    exit()

# 3. CHUNK THE DATA
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
print(f"--- 🔪 Split into {len(chunks)} text chunks ---")

# 4. INITIALIZE DATABASE & EMBEDDINGS
print("--- 💾 Initializing Vector Database... ---")
# WE USE THE NEWER MODEL HERE: text-embedding-004
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Initialize an empty DB first
vector_db = Chroma(
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# 5. SAFE BATCH INSERTION (The Fix)
batch_size = 5  # Process 5 chunks at a time
total_batches = len(chunks) // batch_size + 1

print(f"--- 🐢 Starting Safe Batch Processing ({total_batches} batches) ---")

for i in range(0, len(chunks), batch_size):
    batch = chunks[i: i + batch_size]

    if not batch:
        continue

    try:
        vector_db.add_documents(batch)
        print(f"   ✅ Processed batch {i//batch_size + 1}/{total_batches}")
        time.sleep(2)  # 2-second pause to be kind to the API
    except Exception as e:
        print(f"   ⚠️ Error on batch {i}: {e}")
        time.sleep(10)  # Longer pause if we hit an error

print("--- ✅ Database Built Successfully! ---")
