import os
import sys

# --- STRATEGIC FIX FOR STREAMLIT CLOUD ---
# ChromaDB requires a newer version of SQLite than what Streamlit Cloud provides.
# This code swaps the system's default sqlite3 with the 'pysqlite3-binary' we installed.
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # This handles your local Mac environment where pysqlite3 might not be installed
    # because Macs usually have a modern enough SQLite by default.
    pass

import streamlit as st
# ... rest of your imports (chromadb, etc.) follow here ...
import pandas as pd
import google.generativeai as genai
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

# 1. Page Configuration
st.set_page_config(
    page_title="Michael | MTSS Intelligence",
    page_icon="📈",
    layout="wide"
)

# 2. Secure API Integration (Streamlit Secrets)
try:
    # Authenticate using the key stored in .streamlit/secrets.toml
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ API Key not detected. Check .streamlit/secrets.toml")
    model = None

# 3. Dynamic UI Styling (Light/Dark Switchable)
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Theme Color Mapping
if st.session_state.dark_mode:
    bg_color = "#0F172A"      # Deep Navy
    text_color = "#F8FAFC"    # Crisp White
    card_bg = "#1E293B"       # Slate
    border_color = "#334155"  # Muted Blue/Grey
else:
    bg_color = "#FFFFFF"      # Pure White
    text_color = "#1E293B"    # Deep Slate
    card_bg = "#F8FAFC"       # Light Grey/Blue
    border_color = "#E2E8F0"  # Soft Grey

st.markdown(f"""
    <style>
    /* Global Background and Text */
    .stApp {{ background-color: {bg_color} !important; }}
    p, li, div, span, label, .stMarkdown {{ color: {text_color} !important; }}
    h1, h2, h3 {{ color: {text_color} !important; font-weight: 700 !important; }}
    
    /* KPI Metric & Button Alignment */
    [data-testid="stMetric"], .stButton > button {{
        height: 110px !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        background-color: {card_bg} !important;
    }}
    
    /* Interactive KPI Card Button */
    .stButton > button {{
        width: 100%;
        padding: 0px 20px !important;
        text-align: left !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .stButton > button:hover {{
        border-color: #4F46E5 !important;
        background-color: {"#334155" if st.session_state.dark_mode else "#EEF2FF"} !important;
    }}

    /* Modern Dropdown Menus */
    div[data-baseweb="select"] {{
        border: 1px solid {border_color};
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. Data Engine (Sorted by Priority)


@st.cache_data
def get_data():
    data = {
        'Student Name': ["Alex Rivera", "Jordan Smith", "Taylor Chen", "Morgan Reed", "Casey Blair", "Riley Vance", "Quinn Moore", "Sam Ellis", "Chris Post"],
        'Math Score (%)': [85, 42, 78, 55, 92, 38, 65, 41, 89],
        'Attendance (%)': [98, 75, 95, 82, 99, 70, 88, 72, 94]
    }
    df = pd.DataFrame(data)

    def assign_tier(row):
        # Multi-Tiered System of Supports (MTSS) Logic
        if row['Math Score (%)'] < 50 or row['Attendance (%)'] < 80:
            return "Tier 3: Intensive"
        elif row['Math Score (%)'] < 70 or row['Attendance (%)'] < 90:
            return "Tier 2: Targeted"
        return "Tier 1: Universal"

    df['Support Level'] = df.apply(assign_tier, axis=1)

    # Priority Sort Mapping (Tier 3 is highest priority)
    priority_map = {"Tier 3: Intensive": 0,
                    "Tier 2: Targeted": 1, "Tier 1: Universal": 2}
    df['sort_order'] = df['Support Level'].map(priority_map)
    df = df.sort_values(by='sort_order').drop(columns=['sort_order'])
    return df


# Initialize Data and Session State
df = get_data()
if 'filter_active' not in st.session_state:
    st.session_state.filter_active = False

# 5. PDF Helper Function


def create_pdf(name, content):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=LETTER)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, 750, f"Michael | MTSS Strategic Document: {name}")
    p.setFont("Helvetica", 10)
    y = 720
    for line in content.split('\n'):
        if y < 50:
            p.showPage()
            y = 750
        p.drawString(72, y, line.replace('*', ''))
        y -= 14
    p.save()
    buffer.seek(0)
    return buffer


# 6. Sidebar (With Global Controls)
with st.sidebar:
    st.title("Michael")
    st.caption("AI Product Lab | Mansfield, TX")
    st.divider()

    # Reset View Button
    if st.button("🔄 Reset Global View", icon=":material/refresh:", use_container_width=True):
        st.session_state.filter_active = False
        st.rerun()

    # Dynamic Mode Toggle
    mode_label = "🌙 Switch to Dark Mode" if not st.session_state.dark_mode else "☀️ Switch to Light Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# 7. Dashboard KPI Header
st.title("District Performance Dashboard")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Total Enrollment", len(df))
with k2:
    st.metric("Avg Proficiency", f"{int(df['Math Score (%)'].mean())}%")
with k3:
    critical_count = len(df[df['Support Level'].str.contains("Tier 3")])
    # KPI Card Button for Triage
    if st.button(f"Urgent Interventions\n\n{critical_count} Students", icon=":material/assignment_late:"):
        st.session_state.filter_active = True

st.divider()

# 8. Workflow Tabs
t1, t2 = st.tabs(["📊 Analytics & Roster", "📝 Strategy Builder"])

with t1:
    # Dynamic Filtering Logic
    display_df = df.copy()
    if st.session_state.filter_active:
        display_df = df[df['Support Level'].str.contains("Tier 3")]
        st.info("Filtering active for Tier 3 Intensive Support.",
                icon=":material/info:")

    # Dynamic Charts reflecting filtered data
    st.subheader("Contextual Insights")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Segment Distribution**")
        st.bar_chart(
            display_df['Support Level'].value_counts(), color="#6366F1")
    with g2:
        st.markdown("**Performance Trend**")
        st.line_chart(display_df['Math Score (%)'], color="#10B981")

    st.divider()

    # Professional Font Color Styling
    def style_tiers(val):
        if "Tier 3" in val:
            color = "#D32F2F"  # Modern Slate Red
        elif "Tier 2" in val:
            color = "#D97706"  # Muted Goldenrod
        else:
            color = "#059669"                # Emerald Green
        return f'color: {color}; font-weight: 700;'

    styled_df = display_df.style.map(style_tiers, subset=['Support Level'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

with t2:
    left, right = st.columns([1, 2])
    with left:
        st.subheader("Configuration")
        with st.container(border=True):
            selected = st.selectbox("Target Profile", df['Student Name'])
            s_data = df[df['Student Name'] == selected].iloc[0]
            language = st.selectbox("Outreach Language", [
                                    "English", "Spanish", "Vietnamese", "Mandarin"])
            st.markdown(f"**Current Status:** `{s_data['Support Level']}`")

        st.write("")

        # Action 1: Academic Support Plan
        if st.button("Draft Support Plan", type="primary", icon=":material/description:", use_container_width=True):
            if model:
                with st.spinner("AI Architecting Strategy..."):
                    prompt = f"Act as an expert MTSS coordinator. Create a 3-step math intervention plan for {selected}. Math Score: {s_data['Math Score (%)']}%."
                    res = model.generate_content(prompt)
                    st.session_state.plan, st.session_state.p_name, st.session_state.doc_type = res.text, selected, "Academic Plan"
            else:
                st.error("Gemini API not connected.")

        # Action 2: Multi-Lingual Parent Communication
        if st.button("Draft Parent Outreach", icon=":material/mail:", use_container_width=True):
            if model:
                with st.spinner(f"Translating to {language}..."):
                    prompt = f"Draft an empathetic message to the parents of {selected} in {language} regarding extra math support."
                    res = model.generate_content(prompt)
                    st.session_state.plan, st.session_state.p_name, st.session_state.doc_type = res.text, selected, f"Parent Outreach ({language})"
            else:
                st.error("Gemini API not connected.")

    with right:
        st.subheader("Actionable Document")
        if 'plan' in st.session_state:
            with st.container(border=True):
                st.caption(st.session_state.doc_type)
                st.markdown(st.session_state.plan)

            st.write("")
            pdf = create_pdf(st.session_state.p_name, st.session_state.plan)
            st.download_button(
                f"Export {st.session_state.doc_type}",
                data=pdf,
                file_name=f"MTSS_{st.session_state.p_name}.pdf",
                icon=":material/download:",
                use_container_width=True
            )
        else:
            st.info("Configure settings to generate high-impact student strategies.",
                    icon=":material/clinical_notes:")
