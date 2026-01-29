import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Omni-Agent Platform",
                   layout="wide", initial_sidebar_state="expanded")

# CSS INJECTION: High-Density Enterprise Layout
st.markdown("""
    <style>
        /* 1. Reduce Sidebar Padding */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }
        
        /* 2. Tighten Widget Spacing */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.6rem;
        }

        /* 3. Professional Typography */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 600;
            letter-spacing: -0.5px;
            margin-bottom: 0.5rem !important;
            padding-bottom: 0rem !important;
        }
        
        /* 4. Clean Expanders */
        .stExpander {
            border: 0px solid rgba(0,0,0,0); 
            background-color: transparent;
        }
        
        /* 5. Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---


def get_gemini_response(api_key, prompt, temp=0.3):
    os.environ["GOOGLE_API_KEY"] = api_key
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=temp)
    response = llm.invoke(prompt)
    return response.content


def extract_text_from_pdf(uploaded_file):
    with open("temp_pdf.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    loader = PyPDFLoader("temp_pdf.pdf")
    docs = loader.load()
    return "\n".join([page.page_content for page in docs])


# --- 3. SESSION STATE ---
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "job_desc_text" not in st.session_state:
    st.session_state.job_desc_text = None
if "ops_db" not in st.session_state:
    st.session_state.ops_db = None

# --- 4. SIDEBAR (CLEAN DESIGN) ---
with st.sidebar:
    st.markdown("### Omni-Agent Platform")
    st.caption("Enterprise Edition v1.5")

    with st.expander("Credentials & Settings", expanded=False):
        if "GOOGLE_API_KEY" in st.secrets:
            st.success("System Authenticated")
            api_key = st.secrets["GOOGLE_API_KEY"]
        else:
            api_key = st.text_input("API Key", type="password")

    st.markdown("---")
    st.caption("MODULE SELECTION")
    mode = st.radio(
        "Navigation",
        ["Gap Analysis", "App Generator", "Ops Intelligence", "Research Synth"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.caption("CONTEXT REPOSITORY")
    with st.container(border=True):
        # RESUME UPLOAD
        uploaded_resume = st.file_uploader(
            "Candidate Resume (PDF)", type="pdf")
        if uploaded_resume:
            st.session_state.resume_text = extract_text_from_pdf(
                uploaded_resume)
            st.caption(f"✅ Loaded: {uploaded_resume.name}")

        # JD INPUT WITH ACTION BUTTON
        jd_input = st.text_area("Target Job Description",
                                height=100, placeholder="Paste JD text here...")

        # The User Requested Button
        if st.button("Save Job Description (⌘+Enter)", use_container_width=True):
            if jd_input:
                st.session_state.job_desc_text = jd_input

        # Visual Confirmation Logic
        if jd_input and not st.session_state.job_desc_text:
            st.session_state.job_desc_text = jd_input

        if st.session_state.job_desc_text:
            st.caption("✅ JD Active & Saved")

if not api_key:
    st.warning("System Locked. Please provide API credentials in the sidebar.")
    st.stop()

# --- 5. MAIN CONTENT AREA ---

# MODULE 1: GAP ANALYSIS
if mode == "Gap Analysis":
    st.subheader("Strategic Gap Analysis")
    st.caption("Evaluate candidate fit and authenticity against target role.")

    if st.button("Execute Gap Analysis", type="primary", use_container_width=True):
        if st.session_state.resume_text and st.session_state.job_desc_text:
            with st.status("Analyzing Candidate Profile...", expanded=True) as status:
                st.write("Parsing resume architecture...")
                st.write("Detecting AI generation patterns...")
                st.write("Mapping skills to requirements...")

                prompt = f"""
                Act as a ruthless Executive Recruiter and AI Detector. 
                
                TASK:
                1. Compare the Resume against the JD.
                2. Analyze the Resume for "AI Stench" (patterns that scream ChatGPT-written).
                
                RESUME: 
                {st.session_state.resume_text}
                
                JD: 
                {st.session_state.job_desc_text}
                
                OUTPUT FORMAT (Markdown):
                
                ### 1. 🤖 Authenticity Check (THE MOST IMPORTANT SECTION)
                * **Human Score:** (0-100% - Be brutal. 100% = Purely Human, 0% = Copy/Pasted from ChatGPT).
                * **Verdict:** (e.g., "Authentic Professional", "Hybrid", or "Lazy AI Gen").
                * **Red Flags:** List specific words/phrases that sound robotic (e.g., "delved", "tapestry", "unlocked", "spearheaded", "orchestrated"). If it sounds authentic, praise the specific human details.
                
                ### 2. 🎯 Match Score
                * **Score:** (0-100%)
                * **Summary:** One brutal sentence on if they get the interview.
                
                ### 3. ⚠️ Critical Gaps
                * (Bullet points of missing skills required by the JD)
                
                ### 4. 💡 Strategic Advice
                * (How to fix the gaps and remove the AI-sounding fluff)
                """

                result = get_gemini_response(api_key, prompt)
                status.update(label="Analysis Complete",
                              state="complete", expanded=False)
            st.markdown(result)
        else:
            st.error("Action Required: Upload Resume and JD in the Sidebar.")

# MODULE 2: APP GENERATOR
elif mode == "App Generator":
    st.subheader("Application Material Generator")
    st.caption(
        "Generate ATS-optimized documentation tailored to the specific opportunity.")

    if st.button("Generate Application Package", type="primary", use_container_width=True):
        if st.session_state.resume_text and st.session_state.job_desc_text:
            tab1, tab2 = st.tabs(["Optimized Resume", "Cover Letter"])
            with st.status("Drafting Documents...", expanded=True) as status:

                # RESUME
                st.write("Optimizing for ATS keywords...")
                resume_prompt = f"""
                Role: Expert Resume Writer. Task: Rewrite resume to align with JD.
                Constraints: 
                - Professional tone, NO AI BUZZWORDS (no "delved", "tapestry", "foster").
                - Use strong, simple verbs (Led, Built, Sold).
                - Use JD keywords naturally.
                RESUME: {st.session_state.resume_text} JD: {st.session_state.job_desc_text}
                """
                new_resume = get_gemini_response(
                    api_key, resume_prompt, temp=0.5)

                # COVER LETTER
                st.write("Drafting executive letter...")
                cl_prompt = f"""
                Role: Executive Coach. Task: Write a cover letter connecting user achievements to company pain points.
                Constraints: Direct, professional, no fluff.
                RESUME: {st.session_state.resume_text} JD: {st.session_state.job_desc_text}
                """
                cover_letter = get_gemini_response(
                    api_key, cl_prompt, temp=0.5)
                status.update(label="Generation Complete",
                              state="complete", expanded=False)

            with tab1:
                st.markdown(new_resume)
                st.download_button("Download Resume (.md)",
                                   new_resume, use_container_width=True)
            with tab2:
                st.markdown(cover_letter)
                st.download_button("Download Letter (.md)",
                                   cover_letter, use_container_width=True)
        else:
            st.error("Action Required: Upload Resume and JD in the Sidebar.")

# MODULE 3: OPS INTELLIGENCE
elif mode == "Ops Intelligence":
    st.subheader("Operations Intelligence")
    st.caption("RAG-enabled search across Standard Operating Procedures (SOPs).")

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            manuals = st.file_uploader(
                "Upload SOP Documents", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
        with col2:
            if st.button("Index Docs", use_container_width=True):
                if manuals:
                    with st.status("Indexing Vector Database...", expanded=True) as status:
                        all_docs = []
                        for f in manuals:
                            with open(f"temp_{f.name}", "wb") as file:
                                file.write(f.getbuffer())
                            all_docs.extend(PyPDFLoader(
                                f"temp_{f.name}").load())
                            os.remove(f"temp_{f.name}")
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1000, chunk_overlap=100)
                        chunks = splitter.split_documents(all_docs)
                        embeddings = GoogleGenerativeAIEmbeddings(
                            model="models/text-embedding-004", google_api_key=api_key)
                        st.session_state.ops_db = Chroma.from_documents(
                            chunks, embeddings)
                        status.update(label="Indexing Complete",
                                      state="complete", expanded=False)
                        st.success(
                            f"Knowledge Base Active: {len(chunks)} vectors stored.")

    st.divider()
    query = st.text_input("Operational Query",
                          placeholder="e.g., What is the closing procedure?")

    if st.button("Execute Search", type="primary", use_container_width=True):
        if st.session_state.ops_db and query:
            results = st.session_state.ops_db.similarity_search(query, k=3)
            context = "\n".join([d.page_content for d in results])
            ans = get_gemini_response(
                api_key, f"Context: {context} \n Question: {query}")
            st.markdown(f"### Answer \n {ans}")
            with st.expander("View Source Context"):
                for doc in results:
                    st.caption(doc.page_content[:300] + "...")

# MODULE 4: RESEARCH SYNTH
elif mode == "Research Synth":
    st.subheader("Research Synthesizer")
    st.caption("Multi-document pattern recognition and insight extraction.")

    with st.container(border=True):
        transcripts = st.file_uploader(
            "Upload Transcripts/Logs", type="pdf", accept_multiple_files=True)

    if st.button("Synthesize Insights", type="primary", use_container_width=True):
        if transcripts:
            with st.status("Analyzing Data Patterns...", expanded=True):
                text = ""
                for f in transcripts:
                    text += extract_text_from_pdf(f)
                res = get_gemini_response(
                    api_key, f"Analyze patterns and generate executive summary: {text}")
            st.markdown(res)
