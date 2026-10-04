import ast
import datetime as dt
import json
import operator as op
from functools import lru_cache
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

import planner
import rag
from prompts import ANALYZE, QA, REVIEW, SUMMARY, UNKNOWN

load_dotenv()
ROUTES = {"QA": "retrieve_chunks", "SUMMARIZE": "retrieve_chunks", "STUDY_PLAN": "make_plan",
          "PLAN_MODIFY": "make_plan", "CALC": "calculate", "GENERAL": None}


# ---- LLM + tool -----------------------------------------------------------
@lru_cache
def llm():  # max_retries rides out Groq free-tier 429s
    return ChatGroq(model="openai/gpt-oss-20b", temperature=0, max_retries=4)


def ask(prompt, **v):
    return (prompt | llm()).invoke(v).content


def ask_json(prompt, **v):
    return json.loads((prompt | llm().bind(response_format={"type": "json_object"})).invoke(v).content)


OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg}


def calculator(expr):  # the external tool: safe arithmetic, no eval()
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        if isinstance(n, ast.BinOp): return OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp): return OPS[type(n.op)](ev(n.operand))
        raise ValueError("unsupported")
    return ev(ast.parse(expr, mode="eval").body)


# ---- state + helpers --------------------------------------------------------
class S(TypedDict, total=False):
    query: str; messages: list; args: dict; intents: list; todo: list
    chunks: list; plan: list; calc: str; note: str; answer: str


def history(s):
    return "\n".join(f"{m['role']}: {m['content']}" for m in s.get("messages", [])[-6:]) or "none"


def material(s):
    p = []
    if s.get("chunks"):
        p.append("College documents:\n" + "\n\n".join(
            f"[{c['file']} | {c['url']}] {c['text']}" for c in s["chunks"]))
    if s.get("plan"): p.append("Study plan:\n" + json.dumps(s["plan"]))
    if s.get("calc"): p.append("Calculator: " + s["calc"])
    if s.get("note"): p.append("Note: " + s["note"])
    return "\n\n".join(p)


# ---- nodes ----------------------------------------------------------------
def analyze(s):
    try:
        j = ask_json(ANALYZE, today=dt.date.today(), has_plan=bool(s.get("plan")),
                     history=history(s), query=s["query"])
    except ValueError:  # unparseable JSON -> treat as a college question
        j = {"intents": ["QA"]}
    intents = [i for i in j.get("intents") or [] if i in ROUTES] or ["GENERAL"]
    todo = list(dict.fromkeys(ROUTES[i] for i in intents if ROUTES[i]))
    return {"args": j, "intents": intents, "todo": todo, "chunks": [], "calc": "", "note": ""}


def route(s):
    return (s.get("todo") or ["respond"])[0]


def retrieve_chunks(s):
    k = 6 if "SUMMARIZE" in s["intents"] else 5  # ponytail: small k keeps us under Groq free 8K tokens/min
    q = s["args"].get("search_query") or s["query"]
    return {"chunks": rag.retrieve(q, k), "todo": s["todo"][1:]}


def make_plan(s):
    a, rest = s["args"], s["todo"][1:]
    if "PLAN_MODIFY" in s["intents"] and s.get("plan"):
        return {"plan": planner.modify(ask_json, s["plan"], s["query"]), "todo": rest}
    today = dt.date.today()
    try:
        days = int(a["days"]) if a.get("days") else (dt.date.fromisoformat(a["exam_date"]) - today).days
        hours = float(a.get("hours_per_day") or 0)
    except (KeyError, TypeError, ValueError):
        days, hours = 0, 0
    subjects = a.get("subjects") or []
    if isinstance(subjects, str): subjects = [subjects]
    if not (days > 0 and hours > 0 and subjects):
        return {"note": "Cannot build a plan yet. Ask the student for the missing items: subjects, "
                        "exam date (or number of days) and study hours per day.", "todo": rest}
    days = min(days, 30)  # ponytail: 30-day cap keeps the JSON reply small
    total = calculator(f"{days}*{hours:g}")
    ctx = "\n".join(c["text"] for c in rag.retrieve("semester courses credits " + " ".join(subjects), 4))
    return {"plan": planner.create(ask_json, subjects, days, hours, total, ctx, today + dt.timedelta(1)),
            "todo": rest}


def calculate(s):
    expr = s["args"].get("expression") or ""
    try: r = f"{expr} = {calculator(expr):g}"
    except (ValueError, SyntaxError, KeyError, TypeError, ZeroDivisionError): r = f"could not evaluate '{expr}'"
    return {"calc": r, "todo": s["todo"][1:]}


def respond(s):
    m = material(s)
    if not m and {"QA", "SUMMARIZE"} & set(s["intents"]):
        return {"answer": UNKNOWN}  # nothing retrieved -> no LLM call, no chance to guess
    prompt = SUMMARY if "SUMMARIZE" in s["intents"] else QA
    return {"answer": ask(prompt, history=history(s), query=s["query"], material=m or "none")}


def review(s):
    a = s["answer"]
    if a != UNKNOWN and s.get("chunks"):  # second LLM pass only for answers built from documents
        a = ask(REVIEW, material=material(s), answer=a)
    msgs = s.get("messages", []) + [{"role": "user", "content": s["query"]},
                                    {"role": "assistant", "content": a}]
    return {"answer": a, "messages": msgs}


# ---- graph ----------------------------------------------------------------
g = StateGraph(S)
for fn in (analyze, retrieve_chunks, make_plan, calculate, respond, review):
    g.add_node(fn.__name__, fn)
g.add_edge(START, "analyze")
for n in ("analyze", "retrieve_chunks", "make_plan", "calculate"):
    g.add_conditional_edges(n, route)
g.add_edge("respond", "review")
g.add_edge("review", END)
app = g.compile()
