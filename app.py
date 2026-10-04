import pathlib

import streamlit as st

from graph import app as graph

st.set_page_config(page_title="NMAMIT Academic Assistant")
st.title("🎓 NMAMIT Academic Assistant")
st.caption("Ask about admissions, regulations, exams, courses, placements - or build a study plan.")
with st.sidebar:
    st.write(f"Knowledge base: {len(list(pathlib.Path('data/docs').glob('*')))} documents")
    st.markdown("**Try:**\n- What is the minimum attendance?\n- Which courses are in 4th semester CSE?\n"
                "- Summarize the internship rules\n- Plan DAA and DBMS, exam on 20 Nov, 2 hrs/day\n"
                "- I can't study on Saturday\n- 18 chapters in 9 days, per day?")
    if st.button("New chat"):
        st.session_state.clear(); st.rerun()

if not pathlib.Path("vectorstore/chroma.sqlite3").exists():
    st.warning("Knowledge base is empty. Stop the app and run: python ingest.py")

state = st.session_state.setdefault("state", {})
for m in state.get("messages", []):
    st.chat_message(m["role"]).write(m["content"])

if q := st.chat_input("Ask the assistant..."):
    st.chat_message("user").write(q)
    keep = {k: state[k] for k in ("messages", "plan") if k in state}
    try:
        with st.spinner("Thinking..."):
            out = graph.invoke({**keep, "query": q})
    except Exception as e:  # UI boundary: show Groq/rate-limit errors instead of a stack trace
        st.error(f"Something went wrong: {e}"); st.stop()
    st.session_state.state = out
    with st.chat_message("assistant"):
        st.write(out["answer"])
        urls = sorted({c["url"] for c in out.get("chunks", []) if c["url"]})
        if urls:
            st.caption("Sources: " + " · ".join(urls))
