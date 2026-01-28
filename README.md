# 🚀 My AI Product Management Journey

![Status](https://img.shields.io/badge/Status-Active_Learning-success)
![Role](https://img.shields.io/badge/Target_Role-AI_Product_Manager-blue)
![Stack](https://img.shields.io/badge/Tech-Python_|_Gemini_API_|_Git-yellow)

## 🎯 Objective
To transition from "Zero" to a **Technical AI Product Manager** capable of bridging the gap between engineering and strategy. This repository documents my 6-month self-paced curriculum, focusing on:
- **LLM Mechanics:** Understanding Inference, Context Windows, and Temperature.
- **API Integration:** Building actual Python prototypes using Google Gemini.
- **Product Strategy:** Unit economics, latency analysis, and evaluation frameworks.

---

## 📅 Weekly Progress Log

| Week | Focus Area | Key Deliverables & Code | Status |
| :--- | :--- | :--- | :--- |
| **Week 1** | **The Environment & API Basics** | ✅ `hello_ai.py` (First API Call)<br>✅ `career_coach.py` (System Instructions)<br>✅ GitHub Portfolio Setup | **Completed** |
| **Week 2** | **Prompt Engineering & Logic** | *Resume Analyzer Tool* | **Completed** |
| **Week 3** | **RAG & Embeddings** | *RAG** | **Completed** |
| **Week 4** | **AI Economics & Strategy** | ⏳ *UI* | *In-progress* |
| **Week 5** | **Capstone Project** | 🏆 **The Document Chatbot** (End-to-End App) | *Planned* |

---

## 🛠️ Technical Stack & Tools
* **Language:** Python 3.11+
* **Models:** Google Gemini 2.0 Flash / Pro
* **Editor:** VS Code
* **Version Control:** Git & GitHub CLI

## 📂 Project Highlights

### 1. The Ruthless Career Coach (Week 1)
**File:** `career_coach.py`
* **Goal:** Create a persona-based chatbot using System Instructions.
* **PM Insight:** Learned that "Prompt Engineering" is essentially product requirement writing for the model. Changing the `temperature` variable drastically alters the "creativity" vs. "reliability" of the feature.

---

## My Personal Experience 01/08/2026

I had zero experience with command-line tools, which significantly slowed my progress. When Gemini provided various commands and code snippets, I learned to stay alert: the version it referenced might be outdated, and some packages might already be installed (or incorrectly installed) without my knowledge. As a beginner, understanding this upfront would have saved me considerable time.

My key takeaways: First, be as specific as possible when writing prompts. Second, break large, complex requests into smaller, manageable ones—AI hallucination is a real issue. Third, keep practicing!

*This portfolio is part of a self-directed intensive curriculum to master the Technical & Strategic elements of AI Product Management.*

---
# 🤖 AI Product Development Log

## 📅 Weeks 2 & 3: The Logic & The Brain

### **Week 2: The Logic Layer (The Coach)**
**Goal:** Transform a static script into an adaptive, context-aware agent.  
**Status:** ✅ Completed

#### **1. Core Features Built**
* **Hierarchical Sentiment Analysis:** Implemented a "Gatekeeper" system that classifies user intent in tiers rather than a flat list.
    * *Tier 1:* Broad Sentiment (Positive / Negative / Ambiguous).
    * *Tier 2:* Emotional Specificity (e.g., Frustrated vs. Anxious vs. Defeated).
* **Variable Injection:** Built a "Resume Analyzer" that dynamically inserts user-specific text into the prompt, ensuring the AI never gives generic advice.
* **Tone Adaptation:** The agent now swaps personas (e.g., "Hype Man" vs. "Socratic Coach" vs. "Problem Solver") based on the detected sentiment.

#### **2. Technical Architecture**
* **Logic Flow:** User Input $\rightarrow$ `Tier 1 Classification` $\rightarrow$ `Conditional Logic (If/Else)` $\rightarrow$ `Tier 2 Classification` $\rightarrow$ `Persona Selection` $\rightarrow$ `Final Response`.
* **Optimization:** Moved from hard-coded rules to semantic understanding, allowing the AI to detect "Anxiety" (needs reassurance) distinct from "Frustration" (needs solutions).

#### **3. The "PM" Takeaway**
* **Trade-offs:** We accepted higher latency/cost (3 API calls per user turn) in exchange for significantly higher emotional intelligence and accuracy.
* **Privacy:** Learned that `git rm` doesn't delete history. Implemented the "Nuclear Option" (re-initializing Git) to permanently scrub sensitive user data.

---

### **Week 3: The Data Layer (The Brain)**
**Goal:** Solve "Hallucination" by grounding the AI in private, factual data.  
**Status:** ✅ Completed

#### **1. Core Features Built**
* **RAG (Retrieval-Augmented Generation):** A system that answers questions based *strictly* on uploaded PDF documents, refusing to answer if the data isn't there.
* **Vector Database Integration:** Implemented `ChromaDB` to store text as mathematical embeddings, allowing for semantic search rather than just keyword matching.
* **Manual Retrieval Engine:** Built a custom retrieval loop to bypass broken libraries, giving us full control over the "Context Window."

#### **2. Technical Architecture**
* **Ingestion Pipeline:** `Load PDFs` $\rightarrow$ `Chunking (1000 chars)` $\rightarrow$ `Embedding (text-embedding-004)` $\rightarrow$ `Store in ChromaDB`.
* **Retrieval Loop:** `User Query` $\rightarrow$ `Vector Search (Top 3 Chunks)` $\rightarrow$ `Prompt Injection` $\rightarrow$ `Gemini 1.5 Flash` $\rightarrow$ `Answer`.

#### **3. Key Hurdles & Solutions**
* **⛔ The Context Crash:** We hit the "Token Limit" when trying to read too many files at once.
    * *Fix:* Switched from "Context Stuffing" to **Vector Search** (RAG).
* **⛔ The Speed Trap:** We triggered API rate limits (`429 Resource Exhausted`) during ingestion.
    * *Fix:* Implemented **Manual Batching** with a `time.sleep()` throttle mechanism.
* **⛔ Dependency Hell:** Python 3.13 broke the standard `LangChain` imports.
    * *Fix:* Replaced the "Black Box" library functions with our own **"White Box" Manual RAG** code, improving observability.

#### **4. The "PM" Takeaway**
* **Scalability:** We proved that "Context Stuffing" fails at scale. Vector Search is the only viable path for enterprise-grade data retrieval.
* **White-Box AI:** Building the search logic manually gave us visibility into *why* the AI selects certain answers, transforming "Magic" into "Engineering."