# Test cases

Run `streamlit run app.py` and ask these in order in ONE chat. Fill the Result column (pass/fail + note) and take a screenshot of each.

| # | Type | Query | Expected | Result |
|---|------|-------|----------|--------|
| 1 | Direct | What is the minimum attendance required at NMAMIT? | 85% per subject, up to 10% condonation by the Principal | |
| 2 | Follow-up | What happens if it goes below 75%? | Uses the attendance topic: no SEE, 'N' grade, re-register | |
| 3 | RAG | How are CIE and SEE marks split and what are the pass marks? | 50/50, at least 40% in CIE and SEE | |
| 4 | RAG | Which courses are in the 4th semester of B.Tech CSE? | LAA, DAA, MP&ES, SEPM, DBMS (+ lab), etc. | |
| 5 | Summarize | Summarize the internship requirements for B.Tech students | 5-8 bullets from the internship document | |
| 6 | Unknown | What is the hostel curfew timing? | "I couldn't find this information..." | |
| 7 | Multi-step | Summarize the exam evaluation rules, then make a 7-day plan for DAA and DBMS with 2 hours per day | Summary + 7-day table | |
| 8 | Modify | I can't study on Saturday | Same plan, Saturday marked Rest, topics shifted | |
| 9 | Tool | I have 18 chapters and 9 study days. How many chapters per day? | 2 (calculator) | |

LLM vs RAG comparison: `python compare.py` (writes comparison.md) and paste the table into your report.
