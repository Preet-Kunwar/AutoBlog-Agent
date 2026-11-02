<div align="center">

  <img src="https://img.shields.io/badge/🧠_MULTI--AGENT_SYSTEM-LANGGRAPH_&_GEMINI_PIPELINE-8B5CF6?style=for-the-badge&labelColor=0F172A" alt="Header Badge" />

  <h1>✍️ AI Technical Blog Generator</h1>
  
  <p>
    <b><i>Your Autonomous Multi-Agent Technical Writer — Transform raw topics into structured, grounded, publication-ready Markdown in seconds.</i></b>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph" />
    <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=flat-square&logo=google&logoColor=white" alt="Google Gemini" />
    <img src="https://img.shields.io/badge/Tavily_Search_AI-4F46E5?style=flat-square" alt="Tavily AI" />
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit" />
    <img src="https://img.shields.io/badge/Pydantic_v2-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic v2" />
  </p>

  <sub>
    <a href="#-overview">🌟 Overview</a> •
    <a href="#-why-is-this-project-so-useful">💡 Key Benefits</a> •
    <a href="#️-architecture-blueprint">📐 Architecture</a> •
    <a href="#️-tech-stack--technologies-used">🛠️ Tech Stack</a> •
    <a href="#-core-features-summary">🚀 Core Features</a> •
    <a href="#-getting-started">🏁 Getting Started</a>
  </sub>

</div>

<br />

---

## 🌟 Overview

> ### ✍️ *What is the AI Technical Blog Generator?*
> The **AI Technical Blog Generator** is an autonomous multi-agent content generation platform engineered to produce deep, developer-grade technical articles. Unlike generic monolithic LLM prompts that suffer from hallucination, repetition, and mid-article drift, this system leverages a **fine-tuned LangGraph state machine** powered by **Google Gemini** and **Tavily AI Search**.
>
> It breaks down complex technical writing into an intelligent multi-stage pipeline: evaluating topic freshness upfront, gathering authoritative real-time evidence, engineering a structured multi-task plan, and writing all sections **in parallel** via dynamic map-reduce workers before assembling a unified, publication-ready Markdown file.

<br />

### 🔄 The 4-Stage Agentic Engine

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>🧭 1. Route</h3>
      <p>Uses Gemini with structured outputs to classify the topic into <code>closed_book</code> (evergreen fundamentals), <code>hybrid</code> (practical tools/models), or <code>open_book</code> (recent news/roundups), generating scoped search queries if research is needed.</p>
    </td>
    <td width="25%" valign="top">
      <h3>🔎 2. Research</h3>
      <p>Queries Tavily for authoritative web sources, deduplicating and synthesizing raw content into an <b>EvidencePack</b> with strict recency cutoffs (e.g., 7 days for weekly roundups).</p>
    </td>
    <td width="25%" valign="top">
      <h3>📋 3. Orchestrate</h3>
      <p>Architects a comprehensive outline consisting of 5–9 tailored sections with target word counts, 3–6 concrete bullets, and flags for code snippets, citations, and research requirements.</p>
    </td>
    <td width="25%" valign="top">
      <h3>⚡ 4. Fanout & Reduce</h3>
      <p>Concurrently executes parallel Gemini worker nodes for every section using LangGraph's <code>Send</code> API, then reduces and orders them into a clean Markdown document automatically saved to disk.</p>
    </td>
  </tr>
</table>

---

## 💡 Why is this project so useful?

Traditional AI text generators produce shallow, superficial content lacking real implementation details or accurate source links. This agent solves that with four core pillars:

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>⚡ 1. High-Concurrency Parallel Generation</h3>
      <p>Sections are generated in parallel using a distributed Map-Reduce pattern via LangGraph's <code>Send</code> API, delivering 2,500+ word deep-dive technical articles in seconds rather than waiting through serial generation.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🎯 2. Zero-Hallucination Source Grounding</h3>
      <p>For current events and evolving technologies, claims are strictly anchored to live web evidence from Tavily and cited directly with verifiable Markdown links: <code>([Source](URL))</code>.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>📐 3. Structured Developer-First Quality</h3>
      <p>Sections explicitly enforce actionable developer requirements: minimal working code sketches (MWEs), failure modes, edge cases, cost/performance tradeoffs, and observability tips.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🖥️ 4. Real-Time Streaming & Observability</h3>
      <p>The interactive Streamlit dashboard monitors pipeline execution live step-by-step, providing detailed breakdown tabs for Outline Plans, Synthesized Evidence, Formatted Previews, and Node Logs.</p>
    </td>
  </tr>
</table>

---

## ⚙️ Architecture Blueprint

The system is built on a clear separation of concerns between the **Streamlit Frontend** presentation layer, the **LangGraph Agentic State Machine**, **Google Gemini LLM**, and **Tavily AI Search**.

### 🏛️ Full Project Architecture

<div align="center">
  <img src="Architecture_Diagram.png" alt="System Architecture" width="90%" />
</div>

> 📌 **What this shows:**
> 1. **Presentation Layer (`bwa_frontend.py`):** Accepts user prompts, automatically resolves date context, streams live node progress via `app.stream`, and renders Plan, Evidence, Markdown Preview, and Logs tabs.
> 2. **Router Node (`router_node`):** Evaluates topic volatility upfront and branches conditionally into research or planning.
> 3. **Research Node (`research_node`):** Executes real-time web retrieval via Tavily, synthesizing fresh, deduplicated evidence.
> 4. **Orchestrator Node (`orchestrator_node`):** Deconstructs the topic into a structured multi-task plan with strict section schemas.
> 5. **Worker Pool (`worker_node`):** Fans out dynamically to write all sections simultaneously in pure Markdown.
> 6. **Reducer Node (`reducer_node`):** Reassembles sections in chronological order, saves the `.md` file to disk, and pushes the final article to the UI.

---

## 🛠️ Tech Stack & Technologies Used

<div align="center">

| Layer | Technology | Role in Project |
| :--- | :--- | :--- |
| 🎨 **Frontend UI** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | Interactive dashboard, real-time node streaming & tabbed preview |
| ⚙️ **Agent Orchestration** | ![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white) | StateGraph workflow, conditional routing & dynamic parallel fanout (`Send`) |
| 🧠 **LLM & Reasoning** | ![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat-square&logo=google&logoColor=white) | High-speed inference (`gemini-3.5-flash-lite`), structured output parsing & Markdown synthesis |
| 🌐 **Live Web Search** | ![Tavily AI](https://img.shields.io/badge/Tavily_Search_AI-4F46E5?style=flat-square) | Real-time search engine tailored for AI agent evidence retrieval |
| 📐 **Data Schemas** | ![Pydantic v2](https://img.shields.io/badge/Pydantic_v2-E92063?style=flat-square&logo=pydantic&logoColor=white) | Type-safe structured output validation (`Plan`, `Task`, `RouterDecision`, `EvidencePack`) |
| 📊 **Data Manipulation** | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) | Tabular presentation of planned sections and retrieved evidence sources |
| 🔐 **Config & Environment** | ![Python Dotenv](https://img.shields.io/badge/Dotenv-ECD53F?style=flat-square&logo=python&logoColor=black) | Secure local API credential loading and model selection |

</div>

---

## 🚀 Core Features Summary

* ⚡ **Dynamic Map-Reduce Parallelism:** Sections are generated concurrently using LangGraph's `Send` API, drastically slashing generation latency.
* 🧭 **Adaptive Routing:** Automatically selects between `closed_book` (pure fundamentals), `hybrid` (recent tooling updates), and `open_book` (weekly news roundup).
* 🔎 **Synthesized Evidence Retrieval:** Live Tavily search integration with automated duplicate removal and strict recency constraints.
* 📋 **Architected Section Planning:** Generates 5–9 tailored sections with individual goals, non-overlapping bullets, target word counts, and citation/code requirements.
* 📖 **Formatted Article & Raw Code Views:** Switch between a publication-ready styled reading layout or raw Markdown with automatic word count and estimated reading time.
* 💾 **Instant Markdown Export:** One-click download button and automatic background persistence to disk as `<safe_title_slug>.md`.

---

## 🏁 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your machine.

### 2. Configure Environment Variables
Create a `.env` file in the project root with your API keys:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Set Gemini model (defaults to gemini-3.5-flash-lite)
MODEL_NAME=gemini-2.5-flash

# Optional: Tavily Search API Key (required for open_book and hybrid search modes)
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Install Dependencies
Install all required Python packages:

```powershell
pip install streamlit langgraph langchain-google-genai langchain-community tavily-python pydantic pandas python-dotenv
```

### 4. Run the Application
Launch the Streamlit web dashboard:

```powershell
streamlit run bwa_frontend.py
```

Open your browser at `http://localhost:8501`, enter your topic in the sidebar, and click **🚀 Generate Blog**!
