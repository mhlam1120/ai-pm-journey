import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools import DuckDuckGoSearchRun

# --- 1. CONFIGURATION & DATABASE ---
st.set_page_config(page_title="Omni Agent - Enterprise", layout="wide")

# File path for our "Database"
FEEDBACK_FILE = "feedback.json"


def load_feedback():
    """Loads feedback from the JSON file."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_feedback(rating, text):
    """Saves new feedback to the JSON file."""
    data = load_feedback()
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rating": rating,
        "comment": text
    }
    data.append(new_entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=4)
    return data


def get_average_rating():
    """Calculates the average star rating."""
    data = load_feedback()
    if not data:
        return "New"

    total = sum(d['rating'] for d in data)
    avg = total / len(data)
    return f"{avg:.1f}/5 ⭐"


# --- 2. SETUP AI & TOOLS ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Please enter your Google API Key to continue.")
    st.stop()

os.environ["GOOGLE_API_KEY"] = api_key

# Define the AI Model (Using 1.5-Flash for high limits)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001", temperature=0.3)

# Define Tools
search = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="Web Search",
        func=search.run,
        description="Useful for finding current events, news, and real-time information."
    )
]

# Initialize the Agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# --- 3. UI & STYLING ---
# Custom CSS for consistent button styling across all modes
st.markdown("""
<style>
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #45a049;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar with Rating
col_logo, col_title, col_rating = st.columns([1, 4, 2])
with col_title:
    st.title("🤖 Omni Agent")
    st.caption("Enterprise Edition v1.5")
with col_rating:
    st.markdown(
        f"<h3 style='text-align: right; color: #FFD700;'>{get_average_rating()}</h3>", unsafe_allow_html=True)
    st.caption("User Satisfaction Score")

st.divider()

# --- 4. NAVIGATION ---
mode = st.sidebar.radio("Select Mode",
                        ["1. Chat Agent", "2. Deep Research", "3. Document Analysis",
                            "4. Code Generator", "5. Feedback & Rating"]
                        )

# --- MODE 1: CHAT AGENT ---
if mode == "1. Chat Agent":
    st.subheader("💬 Enterprise Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = agent.run(prompt)
                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Agent Error: {e}")

# --- MODE 2: DEEP RESEARCH ---
elif mode == "2. Deep Research":
    st.subheader("🌍 Deep Research Mode")
    topic = st.text_input(
        "Research Topic", placeholder="e.g., The future of solid-state batteries")

    if st.button("Start Research"):
        if topic:
            with st.spinner(f"Researching '{topic}'..."):
                try:
                    # Multi-step research prompt
                    prompt = f"""
                    Conduct a deep research on: {topic}.
                    1. Search for the latest developments.
                    2. Summarize key trends.
                    3. List major companies involved.
                    4. Provide a market outlook for 2025.
                    Format the output as a professional report with headings.
                    """
                    response = agent.run(prompt)
                    st.markdown("### 📄 Research Report")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"Research Failed: {e}")

# --- MODE 3: DOC ANALYSIS ---
elif mode == "3. Document Analysis":
    st.subheader("📄 Document Intelligence")
    uploaded_file = st.file_uploader(
        "Upload a document (TXT or CSV)", type=["txt", "csv"])

    if uploaded_file:
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        doc_content = stringio.read()

        st.info("Document uploaded successfully. Ask questions below.")
        doc_query = st.text_input("Ask about the document:")

        if st.button("Analyze Document"):
            if doc_query:
                prompt = f"""
                Context from document:
                {doc_content[:10000]}
                
                Question: {doc_query}
                
                Answer based ONLY on the document provided.
                """
                response = llm.invoke(prompt).content
                st.markdown(response)

# --- MODE 4: CODE GENERATOR ---
elif mode == "4. Code Generator":
    st.subheader("💻 Code Architect")
    code_task = st.text_area("Describe the code you need:", height=150)
    language = st.selectbox(
        "Language", ["Python", "JavaScript", "SQL", "HTML/CSS"])

    if st.button("Generate Code"):
        prompt = f"""
        Act as a Senior Software Engineer. Write {language} code for:
        {code_task}
        
        Provide:
        1. The code block.
        2. Brief explanation of how it works.
        """
        response = llm.invoke(prompt).content
        st.markdown(response)

# --- MODE 5: FEEDBACK & RATING ---
elif mode == "5. Feedback & Rating":
    st.subheader("⭐ Rate Your Experience")
    st.markdown(
        "Help us improve the Enterprise Edition. Your feedback is stored securely.")

    with st.container(border=True):
        # Star Rating Input
        rating = st.slider("How would you rate this app?", 1, 5, 5)

        # Feedback Text
        feedback_text = st.text_area("How can I further improve this app? (Optional):",
                                     height=100, placeholder="What features should we add next?")

        # Submit Button (Styled matches others)
        if st.button("Submit Feedback"):
            save_feedback(rating, feedback_text)
            st.success("✅ Thank you! Your feedback has been recorded.")
            time.sleep(1)
            st.rerun()  # Refresh to update the star rating at the top

    # Admin View (Optional - Remove if you want to keep it hidden)
    with st.expander("Admin View: Read Feedback"):
        df = pd.DataFrame(load_feedback())
        if not df.empty:
            st.dataframe(df.sort_values(by="timestamp",
                         ascending=False), use_container_width=True)
        else:
            st.info("No feedback yet.")
