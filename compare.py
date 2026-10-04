"""Basic LLM vs RAG on the same questions:  python compare.py   (writes comparison.md)"""
from graph import app, llm

QUESTIONS = [
    "What is the minimum attendance required at NMAMIT Nitte and what happens below 75%?",
    "How many credits are needed for a B.Tech degree at NMAMIT and what CGPA is required?",
    "Which courses are in the 4th semester of B.Tech CSE at NMAMIT?",
    "How is the SEE question paper structured for theory courses at NMAMIT?",
    "What is the hostel curfew timing at NMAMIT?",
]

with open("comparison.md", "w", encoding="utf-8") as f:
    for q in QUESTIONS:
        print("asking:", q)
        f.write(f"## {q}\n\n**Basic LLM:** {llm().invoke(q).content}\n\n**RAG:** {app.invoke({'query': q})['answer']}\n\n")
print("saved comparison.md")
