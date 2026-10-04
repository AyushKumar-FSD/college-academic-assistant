from langchain_core.prompts import PromptTemplate

T = PromptTemplate.from_template
UNKNOWN = "I couldn't find this information in the available college knowledge base, so I don't want to guess."

ANALYZE = T("""You route requests for the NMAMIT (Nitte, Karkala) academic assistant. Return ONLY a JSON object.
Today: {today}
Student already has a study plan: {has_plan}
Recent chat:
{history}
Student message: {query}

JSON keys:
"intents": ordered list of steps, each one of: QA (question about the college: admissions, fees, regulations, attendance, exams, grading, internships, courses, placements, facilities), SUMMARIZE (summarise a topic or document), STUDY_PLAN (create a study plan), PLAN_MODIFY (change the existing plan), CALC (arithmetic), GENERAL (greeting / anything else). Order steps logically, e.g. SUMMARIZE before STUDY_PLAN.
"search_query": the question rewritten to stand alone (resolve "it", "that", "those" from the chat), or null
"subjects": list of course names or short names the plan is for, exactly as the student wrote them, or null
"exam_date": YYYY-MM-DD or null
"hours_per_day": number or null
"days": number of days for the plan or null
"expression": arithmetic using digits and + - * / ( ) only, for CALC, else null""")

_RULES = f"""Use ONLY the material below. Never invent rules, numbers, dates, fees or names.
If the material does not contain what was asked, say exactly: "{UNKNOWN}"
Name the source document (file name) for facts you give. For greetings or small talk, reply briefly.
Show a study plan as a table (Day | Date | Subject | Topic | Hours) and add one line saying the topics are typical for these courses and should be checked against the official syllabus.
If a calculator result is given, use it. If the note says information is missing, ask the student for it.

Recent chat:
{{history}}
Student: {{query}}

Material:
{{material}}"""

QA = T("You are the academic assistant of NMAM Institute of Technology (NMAMIT), Nitte, part of Nitte (Deemed to be University). Answer clearly and briefly; use bullet points for lists.\n" + _RULES)

SUMMARY = T("You are the academic assistant of NMAM Institute of Technology (NMAMIT), Nitte. Summarise the requested topic in 5-8 short bullet points in plain language.\n" + _RULES)

REVIEW = T("""Check the draft answer against the material. Remove or fix any claim (number, rule, date, name) the material does not support. If everything is supported, return the draft unchanged. Return only the final answer.

Material:
{material}

Draft:
{answer}""")

PLAN = T("""Create a day-by-day study plan. Return ONLY JSON: {{"plan": [{{"day": 1, "subject": "...", "topic": "...", "hours": 2}}]}}
Subjects (may be short names; expand them using the context, e.g. DAA = Design and Analysis of Algorithms): {subjects}
Days available: {days}
Hours per day: {hours} (total {total})
College course information: {context}
Rules: exactly {days} entries; split the total hours across the subjects roughly in proportion to their credits if credits appear in the context, otherwise equally; use typical syllabus topics for each course; the last 1-2 days are revision and practice tests.""")

PLAN_EDIT = T("""Edit this study plan as the student asks. Keep every other entry unchanged and keep the fields day, date, subject, topic, hours.
If a day is blocked, set that entry's topic to "Rest", hours to 0, and push its topic and all later topics one day forward (extend the plan by one day if needed).
Return ONLY JSON: {{"plan": [...]}}
Current plan: {plan}
Request: {request}""")
