"""Offline self-check (no API key, no model download):  python check.py"""
import pathlib

from graph import calculator
from ingest import DOCS, chunks, source_url

assert calculator("18/9") == 2 and calculator("2*(3+4)") == 14
for bad in ("__import__('os')", "2**9", "1/0"):
    try: calculator(bad); raise SystemExit(f"accepted {bad}")
    except (ValueError, SyntaxError, KeyError, TypeError, ZeroDivisionError): pass

assert chunks("   ") == [] and len(chunks("a\n\n" * 600, 900)) > 1

files = sorted(DOCS.glob("*.md"))
assert files, "no documents in data/docs"
for f in files:
    t = f.read_text(encoding="utf-8")
    assert source_url(t).startswith("http"), f"{f.name}: missing Source: line"
    assert chunks(t), f"{f.name}: no chunks"
print(f"ok - {len(files)} docs, {sum(len(chunks(f.read_text(encoding='utf-8'))) for f in files)} chunks")
