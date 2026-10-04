"""Rebuild the vector store from data/docs (.md / .txt / .pdf):  python ingest.py"""
import pathlib
import shutil

import pymupdf

DOCS = pathlib.Path("data/docs")


def chunks(text, size=900):  # pack whole paragraphs up to ~size chars
    out, cur = [], ""
    for p in text.split("\n\n"):
        if cur and len(cur) + len(p) > size:
            out.append(cur.strip()); cur = ""
        cur += p + "\n\n"
    return out + [cur.strip()] if cur.strip() else out


def read(p):
    return "".join(pg.get_text() for pg in pymupdf.open(p)) if p.suffix == ".pdf" else p.read_text(encoding="utf-8")


def source_url(text):
    return next((l[7:].strip() for l in text.splitlines()[:5] if l.startswith("Source:")), "")


def build(col):
    for p in sorted(DOCS.iterdir()):
        if p.suffix not in {".md", ".txt", ".pdf"}: continue
        text = read(p)
        cs = chunks(text)
        if not cs:
            print(f"{p.name}: no text (scanned? needs OCR)"); continue
        title = text.splitlines()[0].lstrip("# ").strip()
        meta = {"file": p.name, "url": source_url(text)}
        col.add(ids=[f"{p.name}-{i}" for i in range(len(cs))],
                documents=[f"[{title}] {c}" for c in cs], metadatas=[meta] * len(cs))
        print(f"{p.name}: {len(cs)} chunks")


if __name__ == "__main__":  # stop the Streamlit app first (Windows locks the store)
    shutil.rmtree("vectorstore", ignore_errors=True)  # rebuild from scratch, no stale chunks
    from rag import collection  # imported after the wipe so the new store is created fresh
    build(collection())
