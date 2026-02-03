from google.api_core.exceptions import ResourceExhausted
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from datetime import datetime
import time
import json
import streamlit as st
import os
import sys


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
        
        /* --- 6. STAR RATING: SURGICAL BUTTON SCALING --- */
        
        /* Target the container just for spacing */
        div[data-testid="stFeedback"] {
            padding: 20px 0 !important;
        }

        /* Target the list inside to spread items out */
        div[data-testid="stFeedback"] > ul {
            justify-content: space-evenly !important; 
            width: 100% !important;
            gap: 20px !important;
        }
        
        /* TARGET THE STARS DIRECTLY (Buttons) */
        div[data-testid="stFeedback"] button {
            transform: scale(3.0) !important; /* 3.0x Size */
            margin: 0 15px !important;       /* Add margin so they don't touch */
        }
        
        /* Fix SVG alignment inside the scaled button */
        div[data-testid="stFeedback"] button > div {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
    </style>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

# FEEDBACK DATABASE FUNCTIONS
FEEDBACK_FILE = "feedback.json"


def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_feedback(rating, improvement, feature):
    data = load_feedback()
    # rating comes from st.feedback as 0-4 index, so we add 1
    actual_rating = rating + 1 if isinstance(rating, int) else 5

    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rating": actual_rating,
        "improvement_feedback": improvement,
        "feature_request": feature
    }
    data.append(new_entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=4)
    return data


def get_average_rating():
    data = load_feedback()
    if not data:
        return "New"
    valid_ratings = [d.get('rating') for d in data if isinstance(
        d.get('rating'), (int, float))]
    if not valid_ratings:
        return "New"
    avg = sum(valid_ratings) / len(valid_ratings)
    # Using HTML span to size the star in the Sidebar
    return f"{avg:.1f}/5 <span style='font-size:18px'>⭐</span>"

# AI FUNCTIONS


def get_gemini_response(api_key, prompt, temp=0.3):
    # Initialize usage counter if not exists
    if "api_usage_count" not in st.session_state:
        st.session_state.api_usage_count = 0

    os.environ["GOOGLE_API_KEY"] = api_key

    # --- SMART EXPONENTIAL BACKOFF WITH VISUAL COUNTDOWN ---
    max_retries = 3
    base_delay = 5  # Start with 5 seconds

    for attempt in range(max_retries):
        try:
            # Increment Counter
            st.session_state.api_usage_count += 1

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", temperature=0.3)
            response = llm.invoke(prompt)
            return response.content

        except ResourceExhausted:
            # If we hit the limit...
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)

                # --- VISUAL COUNTDOWN LOGIC ---
                placeholder = st.empty()  # Create a placeholder to update
                for i in range(wait_time, 0, -1):
                    placeholder.warning(
                        f"⚠️ High Traffic. Retrying in {i} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(1)
                placeholder.empty()  # Clear the message
                # ------------------------------

                continue
            else:
                return "⚠️ **DEMO LIMIT REACHED** ⚠️\n\nThe AI is currently overloaded. Please wait 60 seconds and try again."
        except Exception as e:
            return f"⚠️ **SYSTEM ERROR:** {str(e)}"


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
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "api_usage_count" not in st.session_state:
    st.session_state.api_usage_count = 0

# Store generated docs in session state so edits persist
if "gen_resume" not in st.session_state:
    st.session_state.gen_resume = ""
if "gen_cover_letter" not in st.session_state:
    st.session_state.gen_cover_letter = ""

# --- 4. SIDEBAR (CLEAN DESIGN) ---
with st.sidebar:
    st.markdown("### Omni-Agent Platform")
    # Added unsafe_allow_html to render the bigger star
    st.caption(
        f"Enterprise Edition v4.2 | {get_average_rating()}", unsafe_allow_html=True)

    with st.expander("Credentials & Settings", expanded=False):
        if "GOOGLE_API_KEY" in st.secrets:
            st.success("System Authenticated")
            api_key = st.secrets["GOOGLE_API_KEY"]
        else:
            api_key = st.text_input("API Key", type="password")

    # --- NEW: USAGE TRACKER ---
    if api_key:
        st.markdown("---")
        st.caption("⚡ SYSTEM LOAD (DEMO)")

        # Free Tier Limit is roughly 15 RPM.
        usage = st.session_state.api_usage_count
        limit = 15

        # Calculate percentage for progress bar (cap at 100%)
        pct = min(usage / limit, 1.0)

        st.progress(pct, text=f"{usage} / {limit} Load Units")

        if usage >= limit:
            st.warning("⚠️ High Traffic - System may slow down")

        if st.button("Reset Counter", help="Click this to reset usage count for a new demo"):
            st.session_state.api_usage_count = 0
            st.rerun()
    # --------------------------

    st.markdown("---")
    st.caption("MODULE SELECTION")

    # UPDATED NAMES: "Doc. Generator"
    mode = st.radio(
        "Navigation",
        ["Gap Analysis", "Doc. Generator",
            "SOP Search", "Pattern Finder", "Feedback"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # --- FIXED: CONTEXT REPOSITORY IS NOW GLOBAL (PERSISTENT) ---
    st.caption("CONTEXT REPOSITORY")
    with st.container(border=True):
        uploaded_resume = st.file_uploader(
            "Candidate Resume (PDF)", type="pdf")
        if uploaded_resume:
            st.session_state.resume_text = extract_text_from_pdf(
                uploaded_resume)
            st.caption(f"✅ Loaded: {uploaded_resume.name}")

        # Linked to Session State for Persistence
        jd_input = st.text_area(
            "Target Job Description",
            height=100,
            placeholder="Paste JD text here...",
            value=st.session_state.job_desc_text if st.session_state.job_desc_text else ""
        )

        if st.button("Save Job Description (⌘+Enter)", use_container_width=True):
            if jd_input:
                st.session_state.job_desc_text = jd_input

        if jd_input and not st.session_state.job_desc_text:
            st.session_state.job_desc_text = jd_input

        if st.session_state.job_desc_text:
            st.caption("✅ JD Active & Saved")

if not api_key:
    st.warning("System Locked. Please provide API credentials in the sidebar.")
    st.stop()

# --- 5. MAIN CONTENT AREA ---

# MODULE 1: GAP ANALYSIS (RESTORED PROMPT)
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

# MODULE 2: DOC GENERATOR
elif mode == "Doc. Generator":
    st.subheader("Automated Documentation")
    st.caption("Generate ATS-optimized resumes and cover letters.")

    # 1. GENERATE BUTTON
    if st.button("Generate Documents", type="primary", use_container_width=True):
        if st.session_state.resume_text and st.session_state.job_desc_text:
            with st.status("Drafting Documents...", expanded=True) as status:

                # Resume Gen
                resume_prompt = f"Role: Expert Resume Writer. Rewrite resume for JD. RESUME: {st.session_state.resume_text} JD: {st.session_state.job_desc_text}"
                st.session_state.gen_resume = get_gemini_response(
                    api_key, resume_prompt, temp=0.5)

                # Cover Letter Gen
                cl_prompt = f"Role: Executive Coach. Write cover letter. RESUME: {st.session_state.resume_text} JD: {st.session_state.job_desc_text}"
                st.session_state.gen_cover_letter = get_gemini_response(
                    api_key, cl_prompt, temp=0.5)

                status.update(label="Generation Complete",
                              state="complete", expanded=False)
        else:
            st.error("Action Required: Upload Resume and JD in the Sidebar.")

    # 2. PREVIEW & EDIT AREA (Only shows if content exists)
    if st.session_state.gen_resume:
        st.divider()
        st.markdown("### 📝 Review & Edit")

        tab1, tab2 = st.tabs(["Optimized Resume", "Cover Letter"])

        # --- TAB 1: RESUME EDITOR ---
        with tab1:
            col_edit, col_view = st.columns(2)
            with col_edit:
                st.markdown("**Editor (Markdown)**")
                # Text Area allows editing the AI output
                resume_edit = st.text_area(
                    "Resume Editor", value=st.session_state.gen_resume, height=600, label_visibility="collapsed")
            with col_view:
                st.markdown("**Live Preview**")
                with st.container(border=True, height=600):
                    st.markdown(resume_edit)  # Renders the Edited Text

            st.download_button("Download Final Resume (.md)", resume_edit,
                               file_name="Optimized_Resume.md", use_container_width=True)

        # --- TAB 2: COVER LETTER EDITOR ---
        with tab2:
            col_edit, col_view = st.columns(2)
            with col_edit:
                st.markdown("**Editor (Markdown)**")
                cl_edit = st.text_area(
                    "CL Editor", value=st.session_state.gen_cover_letter, height=600, label_visibility="collapsed")
            with col_view:
                st.markdown("**Live Preview**")
                with st.container(border=True, height=600):
                    st.markdown(cl_edit)

            st.download_button("Download Final Letter (.md)", cl_edit,
                               file_name="Cover_Letter.md", use_container_width=True)

# MODULE 3: SOP SEARCH
elif mode == "SOP Search":
    st.subheader("SOP Knowledge Base")
    st.caption("Ask specific questions across your Standard Operating Procedures.")

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

# MODULE 4: PATTERN FINDER
elif mode == "Pattern Finder":
    st.subheader("Pattern Recognition Engine")
    st.caption("Identify themes and trends across multiple transcripts or logs.")

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

# MODULE 5: FEEDBACK
elif mode == "Feedback":
    st.subheader("User Feedback Loop")
    st.caption("Help us improve the Enterprise Edition.")

    # 0. Check for Success Flag (Displayed after rerun)
    if st.session_state.feedback_submitted:
        st.success("✅ Feedback Recorded! Thank you.")
        st.session_state.feedback_submitted = False  # Reset flag

    # 1. Load data to decide layout
    feedback_data = load_feedback()

    # 2. Logic: Split 60/40 ONLY if feedback exists
    if len(feedback_data) > 0:
        col_form, col_display = st.columns([0.6, 0.4], gap="large")
    else:
        col_form = st.container()
        col_display = None

    # --- LEFT SIDE: THE FORM ---
    with col_form:
        with st.container(border=True):

            # Initialize default rating to 4 (5 stars)
            if "star_rating" not in st.session_state:
                st.session_state.star_rating = 4
            if "imp_input" not in st.session_state:
                st.session_state.imp_input = ""
            if "feat_input" not in st.session_state:
                st.session_state.feat_input = ""

            # A. Interactive Stars
            st.markdown("**System Rating**")
            rating_selection = st.feedback("stars", key="star_rating")

            # B. Text Inputs (Linked to Session State)
            st.markdown("**How can I make this app better?**")
            improvement = st.text_area(
                "Improvement", height=80, label_visibility="collapsed", key="imp_input")

            st.markdown("**What feature should I add next?**")
            feature = st.text_area(
                "Feature", height=80, label_visibility="collapsed", key="feat_input")

            # C. Validation Logic
            is_form_filled = len(improvement.strip()) > 0 and len(
                feature.strip()) > 0

            # D. Callbacks (Runs BEFORE reset)
            def submit_callback():
                # Save
                save_feedback(st.session_state.star_rating,
                              st.session_state.imp_input, st.session_state.feat_input)
                # Clear
                st.session_state.imp_input = ""
                st.session_state.feat_input = ""
                st.session_state.star_rating = 4
                # Set Flag
                st.session_state.feedback_submitted = True

            def cancel_callback():
                st.session_state.imp_input = ""
                st.session_state.feat_input = ""
                st.session_state.star_rating = 4

            # E. Buttons
            b_col1, b_col2 = st.columns(2)

            with b_col1:
                st.button("Cancel", use_container_width=True,
                          on_click=cancel_callback)

            with b_col2:
                st.button("Submit Feedback", type="primary", use_container_width=True,
                          disabled=not is_form_filled, on_click=submit_callback)

    # --- RIGHT SIDE: DISPLAY (SCROLLABLE) ---
    if col_display and feedback_data:
        with col_display:
            st.markdown("### Recent Feedback")

            # THE SCROLLABLE CONTAINER
            with st.container(height=500, border=False):
                for item in reversed(feedback_data):
                    with st.container(border=True):
                        # Header: Stars + Date
                        h_col1, h_col2 = st.columns([2, 1])
                        # Using HTML span to size the stars in the List
                        with h_col1:
                            st.markdown(
                                f"<span style='font-size:20px'>{'⭐' * item['rating']}</span>", unsafe_allow_html=True)
                        with h_col2:
                            st.caption(item['timestamp'])

                        st.divider()
                        st.markdown(
                            f"**Improve:** {item['improvement_feedback']}")
                        st.markdown(f"**Feature:** {item['feature_request']}")
