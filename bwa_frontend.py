from __future__ import annotations

import json
import os
import re
from datetime import date
from typing import Any, Dict, Optional, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Import compiled LangGraph app
# -----------------------------
from bwa_backend import app


# -----------------------------
# Helper Functions
# -----------------------------
def safe_slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9 _-]+", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "blog"


def extract_title_from_md(md: str, fallback: str) -> str:
    """
    Extracts the first '# ' heading from markdown to use as title.
    """
    for line in md.splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            if t:
                return t
    return fallback


def clean_markdown_text(raw_text: str) -> str:
    """
    Cleans raw markdown text, parsing out any Python dict/list repr leftovers
    from Gemini responses like [{'type': 'text', 'text': '...'}] and removing raw wrappers.
    """
    if not raw_text:
        return ""

    import ast

    parts = raw_text.split("\n\n")
    cleaned_parts: List[str] = []
    for part in parts:
        s = part.strip()
        if (s.startswith("[{'type': 'text'") or s.startswith('[{"type": "text"') or s.startswith("[{'type':")):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and "text" in item:
                            cleaned_parts.append(str(item["text"]))
                            continue
            except Exception:
                cleaned_parts.append(part)
        else:
            cleaned_parts.append(part)

    text = "\n\n".join(cleaned_parts).strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def extract_latest_state(current_state: Dict[str, Any], step_payload: Any) -> Dict[str, Any]:
    """
    Safely merges streaming node outputs into the cumulative state dictionary.
    """
    if isinstance(step_payload, dict):
        for node_name, node_output in step_payload.items():
            if isinstance(node_output, dict):
                for k, v in node_output.items():
                    if k == "sections" and isinstance(v, list):
                        existing = current_state.get("sections", [])
                        current_state["sections"] = existing + v
                    else:
                        current_state[k] = v
            else:
                current_state[node_name] = node_output
    return current_state


# -----------------------------
# Streamlit UI Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Technical Blog Writer (Gemini Powered)",
    page_icon="✍️",
    layout="wide",
)

st.title("✍️ AI Technical Blog Generator")
st.caption("Powered by LangGraph, Google Gemini, and Tavily Research (Fine-Tuned Pipeline, Pure Markdown)")

# -----------------------------
# Sidebar: Generate Blog
# -----------------------------
with st.sidebar:
    st.header("📝 Generate Blog")
    topic = st.text_area(
        "Blog Topic / Prompt",
        height=140,
        placeholder="e.g. Self Attention in Transformers: from intuition to implementation",
    )
    run_btn = st.button("🚀 Generate Blog", type="primary", use_container_width=True)


# -----------------------------
# Main Content Tabs
# -----------------------------
if "last_out" not in st.session_state:
    st.session_state["last_out"] = None

if "logs" not in st.session_state:
    st.session_state["logs"] = []

tab_plan, tab_evidence, tab_preview, tab_logs = st.tabs(
    ["🧩 Plan", "🔎 Evidence", "📝 Markdown Preview", "🧾 Logs"]
)


# -----------------------------
# Execution Flow
# -----------------------------
if run_btn:
    if not topic.strip():
        st.warning("Please enter a blog topic before generating.")
        st.stop()

    active_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    if not active_key or active_key == "placeholder-key":
        st.error("Gemini API Key is required. Please set it in your `.env` file.", icon="⚠️")
        st.stop()

    inputs: Dict[str, Any] = {
        "topic": topic.strip(),
        "mode": "",
        "needs_research": False,
        "queries": [],
        "evidence": [],
        "plan": None,
        "as_of": date.today().isoformat(),
        "recency_days": 7,
        "sections": [],
        "final": "",
    }

    current_state: Dict[str, Any] = dict(inputs)
    execution_logs: List[str] = []

    status_box = st.status("Executing LangGraph pipeline with Gemini...", expanded=True)
    progress_placeholder = st.empty()

    try:
        # Stream updates from the LangGraph pipeline
        for step in app.stream(inputs, stream_mode="updates"):
            current_state = extract_latest_state(current_state, step)

            # Identify node that produced update
            if isinstance(step, dict):
                for node_name in step.keys():
                    if node_name == "orchestrator":
                        status_box.write("⚙️ Node completed: `orchestrator`")
                        plan_obj = current_state.get("plan")
                        n_tasks = len(plan_obj.tasks) if plan_obj else 0
                        status_box.write(f"⚡ Generating {n_tasks} sections in parallel with Gemini...")
                    else:
                        status_box.write(f"⚙️ Node completed: `{node_name}`")
                    execution_logs.append(f"[{node_name}] {json.dumps(step[node_name], default=str)[:800]}")

            # Live progress summary
            sections_done = len(current_state.get("sections", []) or [])
            total_tasks = len(current_state.get("plan").tasks) if current_state.get("plan") else 0

            sections_status = (
                f"{sections_done} / {total_tasks}"
                if sections_done == total_tasks and total_tasks > 0
                else (f"{sections_done} / {total_tasks} (generating in parallel...)" if total_tasks else sections_done)
            )

            summary_info = {
                "Topic": topic.strip(),
                "Mode": current_state.get("mode") or "evaluating...",
                "Needs Research": current_state.get("needs_research", False),
                "Queries Generated": len(current_state.get("queries", []) or []),
                "Evidence Collected": len(current_state.get("evidence", []) or []),
                "Outline Tasks Planned": total_tasks,
                "Sections Written": sections_status,
            }
            progress_placeholder.json(summary_info)

        # Save cumulative state to session
        st.session_state["last_out"] = current_state
        st.session_state["logs"].extend(execution_logs)
        status_box.update(label="✅ Blog generation complete!", state="complete", expanded=False)
        st.rerun()

    except Exception as e:
        status_box.update(label=f"❌ Error during execution: {str(e)}", state="error", expanded=True)
        st.error(f"Execution failed: {e}")
        st.session_state["logs"].append(f"[ERROR] {str(e)}")


# -----------------------------
# Render Results
# -----------------------------
out = st.session_state.get("last_out")

if out:
    # 1) Plan Tab
    with tab_plan:
        st.subheader("📋 Blog Post Outline & Plan")
        plan_obj = out.get("plan")

        if not plan_obj:
            st.info("No structured plan available.")
        else:
            if hasattr(plan_obj, "model_dump"):
                plan_dict = plan_obj.model_dump()
            elif isinstance(plan_obj, dict):
                plan_dict = plan_obj
            else:
                plan_dict = json.loads(json.dumps(plan_obj, default=str))

            st.markdown(f"### {plan_dict.get('blog_title', 'Untitled Blog')}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(59, 130, 246, 0.08); border-left: 4px solid #3B82F6; padding: 12px 14px; border-radius: 6px; min-height: 80px;">
                        <div style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #3B82F6; margin-bottom: 4px;">🎯 Target Audience</div>
                        <div style="font-size: 0.92rem; line-height: 1.4; color: inherit;">{plan_dict.get('audience', 'Developers')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 12px 14px; border-radius: 6px; min-height: 80px;">
                        <div style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #10B981; margin-bottom: 4px;">🎭 Writing Tone</div>
                        <div style="font-size: 0.92rem; line-height: 1.4; color: inherit;">{plan_dict.get('tone', 'Technical & Practical')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col3:
                kind_display = str(plan_dict.get("blog_kind", "explainer")).replace("_", " ").title()
                st.markdown(
                    f"""
                    <div style="background-color: rgba(139, 92, 246, 0.08); border-left: 4px solid #8B5CF6; padding: 12px 14px; border-radius: 6px; min-height: 80px;">
                        <div style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #8B5CF6; margin-bottom: 4px;">📂 Post Format</div>
                        <div style="font-size: 0.92rem; font-weight: 600; line-height: 1.4; color: inherit;">{kind_display}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.write("")

            tasks = plan_dict.get("tasks", [])
            if tasks:
                st.write("#### Planned Sections")
                task_rows = []
                for t in tasks:
                    task_rows.append(
                        {
                            "Section #": t.get("id"),
                            "Title": t.get("title"),
                            "Target Words": t.get("target_words"),
                            "Requires Research": "Yes" if t.get("requires_research") else "No",
                            "Requires Citations": "Yes" if t.get("requires_citations") else "No",
                            "Requires Code": "Yes" if t.get("requires_code") else "No",
                            "Tags": ", ".join(t.get("tags") or []),
                        }
                    )
                st.dataframe(pd.DataFrame(task_rows), use_container_width=True, hide_index=True)

                with st.expander("🔍 Detailed Section Goals and Bullets"):
                    for t in tasks:
                        st.markdown(f"**Section {t.get('id')}: {t.get('title')}**")
                        st.markdown(f"- *Goal:* {t.get('goal')}")
                        st.markdown("- *Bullets:*")
                        for b in t.get("bullets", []):
                            st.markdown(f"  - {b}")
                        st.divider()

    # 2) Evidence Tab
    with tab_evidence:
        st.subheader("🔎 Synthesized Evidence & Sources")
        evidence = out.get("evidence") or []
        mode = out.get("mode", "closed_book")

        if not evidence:
            if mode == "closed_book":
                st.info("💡 **Closed Book Mode**: Topic is evergreen concepts/fundamentals. No web research was required.")
            else:
                st.info("No evidence retrieved. Either Tavily API key was not configured or search yielded no results.")
        else:
            st.success(f"Retrieved and synthesized **{len(evidence)} authoritative evidence sources**.")
            evidence_rows = []
            for e in evidence:
                if hasattr(e, "model_dump"):
                    e = e.model_dump()
                evidence_rows.append(
                    {
                        "Title": e.get("title", ""),
                        "Published Date": e.get("published_at") or "Undated",
                        "Source": e.get("source") or "Web",
                        "URL": e.get("url", ""),
                    }
                )
            st.dataframe(pd.DataFrame(evidence_rows), use_container_width=True, hide_index=True)

    # 3) Markdown Preview Tab
    with tab_preview:
        st.subheader("📝 Generated Blog Post")
        final_md_raw = out.get("final") or ""
        final_md = clean_markdown_text(final_md_raw)

        if not final_md:
            st.warning("No generated markdown available yet.")
        else:
            plan_obj = out.get("plan")
            if hasattr(plan_obj, "blog_title"):
                blog_title = plan_obj.blog_title
            elif isinstance(plan_obj, dict):
                blog_title = plan_obj.get("blog_title", "blog")
            else:
                blog_title = extract_title_from_md(final_md, "blog")

            md_filename = f"{safe_slug(blog_title)}.md"

            # Word count & reading time metrics
            word_count = len(re.findall(r"\w+", final_md))
            reading_time = max(1, round(word_count / 200))

            col_meta, col_btn = st.columns([3, 1])
            with col_meta:
                st.caption(f"📊 **Word Count:** {word_count:,} words  ·  ⏱️ **Estimated Read Time:** ~{reading_time} min")
            with col_btn:
                st.download_button(
                    label="⬇️ Download Markdown (.md)",
                    data=final_md.encode("utf-8"),
                    file_name=md_filename,
                    mime="text/markdown",
                    use_container_width=True,
                )

            view_mode = st.radio(
                "Display Mode",
                options=["📖 Formatted Article", "📄 Raw Markdown Code"],
                horizontal=True,
                label_visibility="collapsed",
            )

            st.divider()

            if view_mode == "📖 Formatted Article":
                st.markdown(
                    """
                    <style>
                    .article-box {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                        line-height: 1.75;
                        font-size: 1.05rem;
                        padding: 10px 4px;
                    }
                    .article-box h1 {
                        font-size: 2.1rem;
                        font-weight: 800;
                        margin-top: 0.5rem;
                        margin-bottom: 1.5rem;
                        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
                        padding-bottom: 0.5rem;
                    }
                    .article-box h2 {
                        font-size: 1.55rem;
                        font-weight: 700;
                        margin-top: 2rem;
                        margin-bottom: 1rem;
                        border-bottom: 1px solid rgba(128, 128, 128, 0.15);
                        padding-bottom: 0.3rem;
                    }
                    .article-box h3 {
                        font-size: 1.25rem;
                        font-weight: 600;
                        margin-top: 1.5rem;
                    }
                    .article-box pre {
                        border-radius: 8px;
                        padding: 12px;
                    }
                    .article-box blockquote {
                        border-left: 4px solid #3B82F6;
                        padding-left: 14px;
                        color: #6B7280;
                        font-style: italic;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f'<div class="article-box">\n\n{final_md}\n\n</div>', unsafe_allow_html=True)
            else:
                st.code(final_md, language="markdown")

    # 4) Logs Tab
    with tab_logs:
        st.subheader("🧾 Pipeline Execution Logs")
        all_logs = st.session_state.get("logs", [])
        if not all_logs:
            st.caption("No execution logs recorded yet.")
        else:
            st.text_area(
                "Execution History",
                value="\n\n".join(all_logs[-100:]),
                height=520,
            )

else:
    st.info("👋 Welcome! Enter a topic in the sidebar and click **Generate Blog** to run the agent pipeline.")
