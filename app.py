import streamlit as st
import os
import time

# --- IMPORT YOUR RAG TOOLS ---
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. SETUP PAGE CONFIG
st.set_page_config(page_title="DocuChat AI", page_icon="📚")
st.title("📚 Chat with your PDF")

# 2. SESSION STATE (The Memory)
# Streamlit re-runs the whole script on every click.
# We use 'session_state' to remember the chat history and the database connection.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db" not in st.session_state:
    st.session_state.db = None

# 3. SIDEBAR: SETUP & INGESTION
with st.sidebar:
    st.header("⚙️ Settings")

    # Secure API Key Entry
    api_key = st.text_input("Google API Key", type="password")

    # File Uploader
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file and api_key:
        if st.button("Process Document"):
            with st.spinner("Reading, Chunking, and Embedding..."):
                # Save uploaded file temporarily
                temp_filename = "temp_knowledge.pdf"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # --- WEEK 3 LOGIC HERE ---
                os.environ["GOOGLE_API_KEY"] = api_key

                # A. Load
                loader = PyPDFLoader(temp_filename)
                docs = loader.load()

                # B. Split
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, chunk_overlap=100)
                chunks = text_splitter.split_documents(docs)

                # C. Embed & Store
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/text-embedding-004")

                # We use a temporary in-memory DB for the session
                # (We don't save to disk 'chroma_db' folder to keep the web app fast/simple)
                st.session_state.db = Chroma.from_documents(
                    documents=chunks,
                    embedding=embeddings
                )

                st.success(
                    f"✅ Loaded {len(chunks)} chunks from {uploaded_file.name}!")

# 4. CHAT INTERFACE
# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question about your PDF..."):
    # A. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # B. Generate Response (If DB is ready)
    if st.session_state.db and api_key:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            try:
                # --- WEEK 3 MANUAL RAG LOGIC ---
                # 1. Search
                results = st.session_state.db.similarity_search(prompt, k=3)
                context_text = "\n\n".join(
                    [doc.page_content for doc in results])

                # 2. Prompt
                full_prompt = f"""
                You are a helpful assistant. Answer based ONLY on the context below.
                
                CONTEXT:
                {context_text}
                
                QUESTION:
                {prompt}
                """

                # 3. Generate
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", api_key=api_key)
                response = llm.invoke(full_prompt)

                # 4. Display
                message_placeholder.markdown(response.content)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.content})

                # Optional: Show Sources in an expander
                with st.expander("View Sources"):
                    for i, doc in enumerate(results):
                        st.write(
                            f"**Chunk {i+1}:** {doc.page_content[:200]}...")

            except Exception as e:
                message_placeholder.error(f"Error: {e}")
    else:
        st.error("⚠️ Please upload a PDF and enter your API Key first!")
