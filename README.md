# NMAMIT Academic Assistant

AI-Based College Academic Assistant for NMAM Institute of Technology, Nitte (Nitte DU), built for the L&T EduTech Agentic AI capstone brief.
Stack: Groq `openai/gpt-oss-20b` + LangChain + LangGraph + Chroma + Sentence Transformers + Streamlit.

## Run
```
pip install -r requirements.txt
cp .env.example .env            # add GROQ_API_KEY (free at console.groq.com)
python check.py                 # offline sanity check
python ingest.py                # build the vector store (stop the app first) (downloads the embedding model once)
streamlit run app.py
python compare.py                # basic LLM vs RAG, writes comparison.md
```

## Architecture
```
Student -> Streamlit -> LangGraph
START -> analyze -> route -+-> retrieve_chunks (Chroma RAG) --+
                           +-> make_plan (planner + calculator)+-> respond -> review -> END
                           `-> calculate (calculator tool) ---+
```
Steps chain in the order the analyzer returns them, so one message can search, summarise and plan.
If nothing relevant is retrieved, `respond` returns the "I couldn't find this..." message without calling the LLM.

## Brief requirement -> file
| Requirement | Where |
|---|---|
| Collect college documents | `data/docs/` (11 docs from nitte.edu.in, each has a `Source:` URL) |
| Load, split, embed, store | `ingest.py` -> Chroma in `vectorstore/` |
| RAG pipeline | `rag.py`, `retrieve_chunks` in `graph.py` |
| LangChain prompts + LLM | `prompts.py` (QA, summary, study plan, review), `graph.py` |
| Conversational context | `messages` in graph state, kept by `app.py` |
| External tool | `calculator` in `graph.py` (also used for total study hours) |
| LangGraph nodes | analyze / retrieve_chunks / make_plan / calculate / respond / review |
| Study planner + modification | `planner.py` |
| Unknown questions | `respond` + `review` |
| Testing | `tests.md` |
| LLM vs RAG | `compare.py` |
| UI | `app.py` |

## Add more documents
Drop `.md`, `.txt` or `.pdf` files in `data/docs/` (first line a `# Title`, second line `Source: <url>`) and re-run `python ingest.py`.
Good additions: sem 4 syllabus PDFs from nitte.edu.in/nmamit/syllabus, the academic calendar, hostel rules.

## Notes
- The documents are summaries of public pages on nitte.edu.in collected on 2026-10-04. Always verify fees and rules on the official site.
- The study planner's topics come from typical syllabi unless you ingest the official syllabus.
- Tune `MAX_DIST` in `rag.py` if real questions return "not found" (raise it) or unrelated chunks sneak in (lower it).
