# 🎓 NMAMIT Academic Assistant

An AI-powered academic assistant for **NMAM Institute of Technology (NMAMIT), Nitte**, built as an Agentic AI/RAG application.

The application helps students:

- Ask questions about admissions, fees, attendance, examinations, regulations, courses, internships, placements, and student facilities.
- Summarize information from the college knowledge base.
- Create multi-day study plans.
- Modify an existing study plan using natural-language requests.
- Perform safe arithmetic calculations.
- Maintain conversational context within a chat session.
- Refuse to guess when the required college information is not present in the knowledge base.

The project uses **Groq + LangChain + LangGraph + ChromaDB + Sentence Transformers + Streamlit**.

---

## 1. Project at a glance

| Item | Details |
|---|---|
| Application | NMAMIT Academic Assistant |
| UI | Streamlit |
| LLM | Groq `openai/gpt-oss-20b` |
| Agent orchestration | LangGraph |
| Prompt/LLM framework | LangChain |
| Vector database | ChromaDB |
| Embedding model | `all-MiniLM-L6-v2` |
| Document formats | Markdown, TXT, PDF |
| Knowledge base | 11 college documents |
| Main entry point | `app.py` |
| Local vector-store builder | `ingest.py` |
| RAG implementation | `rag.py` |
| Agent graph | `graph.py` |
| Study planner | `planner.py` |
| Prompts | `prompts.py` |
| Testing | `check.py`, `tests.md` |
| LLM-vs-RAG comparison | `compare.py` |
| Deployment | Streamlit Community Cloud |

---

# 2. Main features

## 2.1 College question answering

Students can ask questions such as:

```text
What is the minimum attendance required at NMAMIT?
```

```text
Which courses are in 4th semester B.Tech CSE?
```

```text
How are CIE and SEE marks split?
```

The application retrieves relevant information from the college knowledge base before generating an answer.

---

## 2.2 Document summarization

The assistant can summarize information from the knowledge base.

Example:

```text
Summarize the internship requirements for B.Tech students.
```

The summarization flow retrieves relevant college documents and asks the LLM to produce a concise summary.

---

## 2.3 Study-plan generation

The assistant can create a study schedule based on:

- Subjects
- Number of days or examination date
- Study hours per day
- Existing plan context

Example:

```text
Plan DAA and DBMS, exam on 20 Nov, 2 hrs/day.
```

The generated plan contains:

- Day
- Date
- Subject
- Topic
- Hours

The planner also uses college course information retrieved from the knowledge base where available.

> Study-plan topics are generated from the available course context and typical syllabus topics. They should be checked against the official syllabus.

---

## 2.4 Study-plan modification

The assistant can modify a previously generated plan.

Example:

```text
I can't study on Saturday.
```

The planner can mark the blocked day as rest and move later topics forward.

---

## 2.5 Calculator tool

The application contains a safe arithmetic calculator.

Example:

```text
I have 18 chapters and 9 study days. How many chapters per day?
```

The calculator evaluates arithmetic expressions without using Python `eval()`.

Supported operators include:

```text
+
-
*
/
()
```

---

## 2.6 Conversation memory

The Streamlit interface keeps recent conversation messages in the Streamlit session state.

This allows follow-up questions such as:

```text
What is the minimum attendance?
```

followed by:

```text
What happens if it goes below that?
```

The analyzer uses recent chat history to resolve references such as "it", "that", and "those".

The **New chat** button clears the current session state.

---

## 2.7 Knowledge-grounded answers

The assistant is intentionally designed not to invent college-specific facts.

If a college question cannot be answered from the retrieved knowledge base, it uses:

```text
I couldn't find this information in the available college knowledge base, so I don't want to guess.
```

For document-based answers, a review step checks the generated answer against the retrieved material and removes unsupported claims.

---

# 3. Architecture

The high-level flow is:

```text
                    ┌─────────────────────┐
                    │      Student        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Streamlit UI    │
                    │       app.py        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     LangGraph       │
                    │      graph.py       │
                    └──────────┬──────────┘
                               │
                               ▼
                         ┌───────────┐
                         │  analyze  │
                         └─────┬─────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
              ▼                ▼                 ▼
     ┌────────────────┐ ┌──────────────┐ ┌──────────────┐
     │ retrieve_chunks│ │  make_plan   │ │  calculate   │
     │    RAG/Chroma  │ │   planner    │ │    tool      │
     └───────┬────────┘ └──────┬───────┘ └──────┬───────┘
             │                 │                │
             └─────────────────┼────────────────┘
                               ▼
                         ┌───────────┐
                         │  respond  │
                         └─────┬─────┘
                               ▼
                         ┌───────────┐
                         │  review   │
                         └─────┬─────┘
                               ▼
                         ┌───────────┐
                         │    END    │
                         └───────────┘
```

---

# 4. Request-processing flow

When a student submits a message, the following process occurs.

## Step 1 — Streamlit receives the question

`app.py` receives the student's message and passes the current conversation state and query to the LangGraph application.

---

## Step 2 — Intent analysis

The `analyze` node in `graph.py` asks the Groq LLM to classify the request.

Possible intents include:

```text
QA
SUMMARIZE
STUDY_PLAN
PLAN_MODIFY
CALC
GENERAL
```

It also extracts information needed by downstream nodes, such as:

- Search query
- Subjects
- Exam date
- Number of days
- Hours per day
- Arithmetic expression

---

## Step 3 — Routing

The graph maps each intent to an appropriate node.

```text
QA          → retrieve_chunks
SUMMARIZE   → retrieve_chunks
STUDY_PLAN  → make_plan
PLAN_MODIFY → make_plan
CALC        → calculate
GENERAL     → respond
```

The graph supports multiple intents in a single request and processes them in order.

For example:

```text
Summarize the exam rules, then make a 7-day DAA study plan.
```

can perform retrieval first and then create the plan.

---

# 5. RAG pipeline

The Retrieval-Augmented Generation pipeline consists of:

```text
College documents
      │
      ▼
   ingest.py
      │
      ▼
Paragraph-based chunking
      │
      ▼
Sentence Transformer embeddings
      │
      ▼
     Chroma
      │
      ▼
Similarity search
      │
      ▼
Relevant chunks
      │
      ▼
Groq LLM
      │
      ▼
Grounded answer
```

## 5.1 Source documents

The knowledge base is stored in:

```text
data/docs/
```

The project currently contains 11 documents covering areas such as:

- NMAMIT overview
- Nitte University
- Admissions
- Fees
- Academic regulations
- Examination guidelines
- Internship guidelines
- CSE curriculum
- Placements
- Student support facilities
- Student FAQ

---

## 5.2 Document chunking

`ingest.py` reads supported documents and divides their content into chunks of approximately 900 characters while attempting to keep paragraphs together.

Supported formats:

```text
.md
.txt
.pdf
```

---

## 5.3 Embeddings

The application uses:

```text
all-MiniLM-L6-v2
```

through Sentence Transformers.

The embedding model converts document chunks and search queries into vectors so semantically similar content can be retrieved.

---

## 5.4 ChromaDB

The vector database is stored locally in:

```text
vectorstore/
```

The collection is named:

```text
docs
```

The project uses cosine similarity.

The retrieval distance threshold is controlled by:

```python
MAX_DIST = 0.65
```

in `rag.py`.

If retrieved chunks are beyond the configured threshold, they are discarded.

---

# 6. Automatic knowledge-base creation

The vectorstore is intentionally excluded from Git because it is generated data.

`.gitignore` contains:

```text
vectorstore/*
!vectorstore/.gitkeep
```

This creates an important deployment requirement: a fresh Streamlit Cloud environment does not contain the local Chroma database.

The current `app.py` solves this by checking for:

```text
vectorstore/chroma.sqlite3
```

before importing the graph.

If the file does not exist, the application automatically runs:

```text
python ingest.py
```

and builds the knowledge base from `data/docs/`.

Therefore:

```text
Fresh deployment
      │
      ▼
No vectorstore
      │
      ▼
app.py detects missing database
      │
      ▼
ingest.py runs automatically
      │
      ▼
Chroma vectorstore is created
      │
      ▼
Application starts normally
```

This is especially important for Streamlit Community Cloud.

---

# 7. Project structure

```text
college-academic-assistant/
│
├── data/
│   └── docs/
│       ├── 01_nmamit_overview.md
│       ├── 02_nitte_university.md
│       ├── 03_admissions.md
│       ├── 04_fees.md
│       ├── 05_academic_regulations.md
│       ├── 06_examination_guidelines.md
│       ├── 07_internship_guidelines.md
│       ├── 08_cse_curriculum.md
│       ├── 09_placements.md
│       ├── 10_student_support_facilities.md
│       └── 11_student_faq.md
│
├── vectorstore/
│   └── .gitkeep
│
├── app.py
├── graph.py
├── rag.py
├── ingest.py
├── planner.py
├── prompts.py
├── check.py
├── compare.py
├── tests.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# 8. File-by-file explanation

## `app.py`

The Streamlit frontend.

Responsibilities:

- Configure the Streamlit page.
- Display the application title and sidebar.
- Display chat history.
- Accept user questions.
- Automatically build the vectorstore when missing.
- Invoke the LangGraph application.
- Display the assistant's answer.
- Display source URLs returned by retrieval.
- Handle UI-level errors.
- Provide the New Chat button.

---

## `graph.py`

The central agent workflow.

Responsibilities:

- Load environment variables.
- Configure the Groq LLM.
- Define the calculator.
- Define LangGraph state.
- Analyze user intent.
- Route requests.
- Retrieve knowledge-base chunks.
- Create or modify study plans.
- Perform calculations.
- Generate responses.
- Review document-grounded answers.
- Maintain conversation messages.

---

## `rag.py`

The retrieval layer.

Responsibilities:

- Create/access the persistent Chroma client.
- Configure the Sentence Transformer embedding function.
- Access the `docs` collection.
- Search for semantically relevant chunks.
- Filter results using `MAX_DIST`.

---

## `ingest.py`

The knowledge-base ingestion pipeline.

Responsibilities:

1. Find documents in `data/docs/`.
2. Read Markdown, TXT, and PDF files.
3. Extract PDF text using PyMuPDF.
4. Split documents into chunks.
5. Extract the `Source:` URL.
6. Generate embeddings through the Chroma embedding function.
7. Store chunks and metadata in Chroma.

Running it directly rebuilds the vectorstore from scratch.

---

## `planner.py`

Study-plan logic.

Contains:

- `create()` for generating a new study plan.
- `modify()` for modifying an existing plan.

The planner uses prompts from `prompts.py`.

---

## `prompts.py`

Contains the application's prompt templates.

Important prompts include:

```text
ANALYZE
QA
SUMMARY
REVIEW
PLAN
PLAN_EDIT
```

The prompts define how the LLM should:

- classify requests,
- answer college questions,
- summarize material,
- review factual grounding,
- create study plans,
- modify study plans.

---

## `check.py`

Offline sanity checks.

It verifies:

- Calculator behavior.
- Calculator rejection of unsafe expressions.
- Chunking behavior.
- Presence of source URLs.
- Presence of documents.
- Ability to create chunks.

It does not require a Groq API key.

---

## `compare.py`

Runs a basic comparison between:

```text
Basic LLM
vs.
RAG application
```

It uses a predefined set of college-related questions and writes the result to:

```text
comparison.md
```

This can be useful for demonstrating why retrieval improves answers for college-specific questions.

---

## `tests.md`

Contains manual end-to-end test cases for:

- Direct questions
- Follow-up questions
- RAG questions
- Summarization
- Unknown questions
- Multi-step requests
- Study-plan modification
- Calculator usage

---

## `requirements.txt`

Defines the main Python dependencies:

```text
langchain-groq
langgraph
chromadb
sentence-transformers
pymupdf
streamlit
python-dotenv
```

---

# 9. Local setup

## Prerequisites

Recommended:

- Python 3.12
- Git
- Internet connection for installing packages and downloading the embedding model
- A Groq API key

The project was developed and tested with Python 3.12.

---

## Windows PowerShell

Clone the repository:

```powershell
git clone https://github.com/AyushKumar-FSD/college-academic-assistant.git
cd college-academic-assistant
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell activation is blocked by execution policy, activate the environment using the appropriate local Python/PowerShell configuration.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Verify dependencies:

```powershell
python -m pip check
```

---

## macOS / Linux

Clone the repository:

```bash
git clone https://github.com/AyushKumar-FSD/college-academic-assistant.git
cd college-academic-assistant
```

Create a virtual environment:

```bash
python3.12 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Verify dependencies:

```bash
python -m pip check
```

---

# 10. Configure the Groq API key

Copy the example environment file.

### Windows

```powershell
Copy-Item .env.example .env
```

### macOS/Linux

```bash
cp .env.example .env
```

Open `.env` and set:

```env
GROQ_API_KEY=your_actual_groq_api_key
```

Never commit `.env` to Git.

The repository's `.gitignore` already excludes:

```text
.env
```

---

# 11. Build the knowledge base locally

You can explicitly build the vectorstore with:

```bash
python ingest.py
```

The command:

- Reads the documents.
- Creates chunks.
- Downloads the embedding model the first time if necessary.
- Creates the Chroma database.
- Stores the document embeddings.

On the first run, downloading the Sentence Transformer model may take some time.

After ingestion, you can verify the knowledge base with:

```bash
python check.py
```

A successful check reports the number of documents and chunks found.

---

# 12. Run the application locally

Start Streamlit:

```bash
streamlit run app.py
```

Streamlit will display a local URL, normally similar to:

```text
http://localhost:8501
```

Open that URL in your browser.

### Important

The current `app.py` automatically builds the knowledge base if the Chroma database is missing.

Therefore, on a fresh environment you can normally start directly with:

```bash
streamlit run app.py
```

The first startup can take longer because the application may need to:

1. Install dependencies.
2. Download the embedding model.
3. Build the Chroma vectorstore.

---

# 13. How to use the application

Once the UI opens, ask a normal question in the chat box.

Examples:

### College information

```text
What is the minimum attendance required at NMAMIT?
```

### Curriculum

```text
Which courses are in the 4th semester of B.Tech CSE?
```

### Summary

```text
Summarize the internship requirements for B.Tech students.
```

### Study planning

```text
Plan DAA and DBMS for 7 days with 2 hours per day.
```

### Calculator

```text
I have 18 chapters and 9 study days. How many chapters per day?
```

### Plan modification

After creating a plan:

```text
I can't study on Saturday.
```

### Unknown information

Ask about information that is not in the knowledge base. The assistant should avoid inventing an answer.

---

# 14. Running the tests

## Offline checks

Run:

```bash
python check.py
```

This checks the calculator, chunking logic, document availability, and source metadata.

---

## Manual application tests

Start the application:

```bash
streamlit run app.py
```

Then use the scenarios in:

```text
tests.md
```

The test suite covers:

1. Direct college questions.
2. Follow-up questions.
3. RAG retrieval.
4. Summarization.
5. Unknown information.
6. Multi-step requests.
7. Study-plan modification.
8. Calculator/tool use.

---

## LLM vs RAG comparison

Run:

```bash
python compare.py
```

This creates:

```text
comparison.md
```

The file contains responses from:

- Basic LLM
- RAG-enabled application

for the same predefined questions.

---

# 15. Adding or updating college documents

The college knowledge base is stored in:

```text
data/docs/
```

Supported formats:

```text
.md
.txt
.pdf
```

These files are the **source documents** used by the RAG system.

### Adding a new document

1. Add the new document to:

```text
data/docs/
```

For example:

```text
data/docs/
├── 01_nmamit_overview.md
├── ...
├── 11_student_faq.md
├── 12_academic_calendar.md
├── 13_hostel_guidelines.pdf
└── 14_scholarships.md
```

2. For Markdown or text files, it is recommended that the beginning follows this pattern:

```text
# Document Title
Source: https://example.com/official-page
```

The `Source:` URL is stored as document metadata and can be shown in the application's source section.

3. Rebuild the vectorstore:

```bash
python ingest.py
```

`ingest.py` rebuilds the vectorstore from **all documents** in `data/docs/`, so you do not need to manually add the new document to ChromaDB.

4. Verify the knowledge base:

```bash
python check.py
```

5. Test the application:

```bash
streamlit run app.py
```

6. If everything works, commit and push the source-document change:

```bash
git add data/docs/
git commit -m "Add new knowledge-base document"
git push
```

7. After the GitHub push, Streamlit Community Cloud will redeploy the application. The deployed application automatically rebuilds the vectorstore when the generated vectorstore is not present.

### Updating an existing document

The same workflow applies when an existing college document changes:

```text
Edit document
     ↓
Save in data/docs/
     ↓
python ingest.py
     ↓
python check.py
     ↓
Test with Streamlit
     ↓
git add / commit / push
     ↓
Streamlit Cloud redeploys
```

### Important: do not edit vectorstore manually

Use this distinction:

```text
data/docs/       → source knowledge; commit these files
vectorstore/     → generated ChromaDB data; do not commit manually
```

The `vectorstore/` directory is intentionally ignored by Git. Do not add new documents directly inside it.

### Recommended sources

Prefer official NMAMIT/Nitte sources for:

- Academic regulations
- Fees
- Examination rules
- Curriculum
- Academic calendar
- Admissions
- Internship requirements
- Placement information
- Student facilities

Always verify time-sensitive rules, fees, deadlines, and regulations against the current official source.

# 16. Git workflow

Check changes:

```bash
git status
```

Review changes:

```bash
git diff
```

Stage a file:

```bash
git add README.md
```

Commit:

```bash
git commit -m "Update project documentation"
```

Push:

```bash
git push
```

The vectorstore is intentionally ignored and should not normally be committed.

---

# 17. Streamlit Community Cloud deployment

The application can be deployed using **Streamlit Community Cloud**.

The important deployment design is that the Chroma vectorstore does not need to be committed to Git. The application automatically rebuilds it when the deployment environment does not contain `vectorstore/chroma.sqlite3`.

---

## Step 1 — Push the project to GitHub

Make sure the latest code is pushed:

```bash
git status
git add .
git commit -m "Prepare project for deployment"
git push
```

The repository used for this project is:

```text
AyushKumar-FSD/college-academic-assistant
```

---

## Step 2 — Open Streamlit Community Cloud

Open:

https://share.streamlit.io/

Sign in using GitHub.

---

## Step 3 — Create a new app

Choose:

```text
Create app
```

Select:

```text
Repository:
AyushKumar-FSD/college-academic-assistant
```

Set:

```text
Branch:
main
```

Set:

```text
Main file path:
app.py
```

---

## Step 4 — Choose an app URL

You can use the generated URL or choose a custom available subdomain.

For this deployment, an example URL is:

```text
https://nmamit-college-academic-assistant.streamlit.app/
```

---

## Step 5 — Configure Advanced Settings

Open:

```text
Advanced settings
```

### Python version

Use:

```text
Python 3.12
```

This matches the local development environment used for the project.

### Secrets

Add the Groq API key using TOML format:

```toml
GROQ_API_KEY = "YOUR_ACTUAL_GROQ_API_KEY"
```

Do not put the actual key in:

- GitHub source code
- `README.md`
- `.env.example`
- screenshots
- public documentation

Streamlit Secrets should be used for the deployed application's secret configuration.

---

## Step 6 — Deploy

Click:

```text
Deploy
```

Streamlit will:

1. Clone the GitHub repository.
2. Install dependencies from `requirements.txt`.
3. Start `app.py`.
4. Detect that the vectorstore is missing.
5. Run `ingest.py` automatically.
6. Download/load the embedding model.
7. Build the Chroma knowledge base.
8. Start the Streamlit interface.

The first deployment may take longer than later starts.

---

# 18. Updating the deployed application

After changing the project:

```bash
git add .
git commit -m "Describe the change"
git push
```

Streamlit Community Cloud detects the repository update and redeploys the application.

Typical workflow:

```text
Edit code
   ↓
Test locally
   ↓
git status
   ↓
git diff
   ↓
git add
   ↓
git commit
   ↓
git push
   ↓
Streamlit Cloud redeploys
```

---

# 19. Streamlit deployment troubleshooting

## Problem: application fails because the API key is missing

Check Streamlit:

```text
Advanced settings → Secrets
```

Make sure this exists:

```toml
GROQ_API_KEY = "your_actual_key"
```

Do not put the key in GitHub.

---

## Problem: knowledge base is empty

The application is designed to automatically run ingestion when:

```text
vectorstore/chroma.sqlite3
```

does not exist.

Check that the deployment contains:

```text
data/docs/
```

and that the document files are present in Git.

If documents were not committed, ingestion cannot build the knowledge base.

---

## Problem: deployment takes a long time

The first deployment may need to:

- install large ML dependencies,
- download the Sentence Transformer model,
- generate embeddings for all documents.

This can make the first startup considerably slower than subsequent application interactions.

---

## Problem: answers are not retrieved

Check:

```python
MAX_DIST = 0.65
```

in `rag.py`.

A lower threshold is stricter and may reject relevant results.

A higher threshold can retrieve more results but may also introduce unrelated chunks.

Tune it using representative questions from `tests.md`.

---

## Problem: college information is outdated

Update the relevant files in:

```text
data/docs/
```

Then rebuild:

```bash
python ingest.py
```

Commit the updated source documents and push them to GitHub.

Streamlit will redeploy the application and rebuild the vectorstore in the new environment.

---

# 20. Security considerations

## Never commit the API key

Keep the real key only in:

```text
.env
```

for local development and Streamlit Secrets for deployment.

The repository contains only:

```text
.env.example
```

with a placeholder.

---

## Do not commit the generated vectorstore

The project intentionally ignores:

```text
vectorstore/*
```

because the vectorstore is generated from the source documents.

---

## Calculator safety

The calculator does not use:

```python
eval()
```

Instead, it parses an arithmetic expression using Python's AST and permits only a restricted set of arithmetic operations.

This prevents arbitrary Python code from being executed through the calculator input.

---

# 21. Design decisions

## Why RAG?

A general-purpose LLM may know broad information but should not be trusted to reliably provide institution-specific details such as:

- Attendance requirements
- Examination rules
- Fees
- Course structures
- Internship rules

RAG supplies relevant college documents to the model before answering.

---

## Why Chroma?

Chroma provides a simple local persistent vector database suitable for this project.

It also works well for a relatively small academic document collection.

---

## Why Sentence Transformers?

The `all-MiniLM-L6-v2` model provides lightweight semantic embeddings suitable for retrieving relevant chunks from the college documents.

---

## Why LangGraph?

LangGraph makes the multi-step workflow explicit.

Instead of treating every user message as one LLM call, the application can:

```text
Analyze
   ↓
Route
   ↓
Retrieve / Plan / Calculate
   ↓
Respond
   ↓
Review
```

This makes the agent flow easier to extend and reason about.

---

## Why a review node?

The application performs a second LLM pass for answers built from retrieved college documents.

The review checks the draft against the retrieved material and removes unsupported claims.

This is an additional safeguard against hallucinated college-specific facts.

---

# 22. Current limitations

The project is intentionally focused on the supplied knowledge base.

Important limitations include:

1. The assistant cannot know information that is absent from the knowledge base.
2. College rules and fees can change, so source documents must be updated.
3. Study-plan topics may be typical topics rather than an exact official syllabus unless the official syllabus has been ingested.
4. Groq API usage is subject to the limits and availability of the selected Groq service/model.
5. Streamlit Community Cloud resources and availability are subject to Streamlit's current service policies.
6. The Chroma vectorstore is generated locally/deployment-time rather than stored in Git.
7. PDF ingestion depends on the PDF containing extractable text; scanned PDFs may require OCR.

---

# 23. Recommended future improvements

Possible future enhancements include:

- Add more official NMAMIT documents.
- Add the academic calendar.
- Add official semester syllabus PDFs.
- Add better document versioning.
- Add document update dates.
- Add source citations per individual answer claim.
- Add authentication if the application becomes private.
- Add automated evaluation for RAG quality.
- Add automated tests for graph routing.
- Add feedback buttons for answer quality.
- Add caching for model and embedding initialization.
- Add a more structured source viewer.
- Add support for additional universities/departments through separate knowledge bases.

---

# 24. Quick command reference

## Setup

```bash
python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install:

```bash
python -m pip install -r requirements.txt
```

Check:

```bash
python -m pip check
```

---

## Environment

```text
.env
```

```env
GROQ_API_KEY=your_actual_groq_api_key
```

---

## Knowledge base

```bash
python ingest.py
```

```bash
python check.py
```

---

## Run application

```bash
streamlit run app.py
```

---

## Comparison

```bash
python compare.py
```

---

## Git

```bash
git status
git diff
git add .
git commit -m "Your message"
git push
```

---

# 25. Example end-to-end workflow

A new developer can get the project running with:

```bash
git clone https://github.com/AyushKumar-FSD/college-academic-assistant.git
cd college-academic-assistant
python -m venv venv
```

Activate the environment and install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=your_actual_groq_api_key
```

Verify the project:

```bash
python check.py
```

Build the knowledge base:

```bash
python ingest.py
```

Run the application:

```bash
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal and start asking questions.

---

# 26. Final project flow

The complete system can be summarized as:

```text
                 ┌───────────────────┐
                 │  College Sources  │
                 └─────────┬─────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  ingest.py   │
                    └──────┬───────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Sentence Transformers│
                └──────────┬───────────┘
                           │
                           ▼
                    ┌────────────┐
                    │  ChromaDB  │
                    └─────┬──────┘
                          │
                          │ retrieval
                          ▼
Student → Streamlit → LangGraph → Relevant Context
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          QA/Summary   Planner    Calculator
             │           │           │
             └───────────┼───────────┘
                         ▼
                    Groq LLM
                         │
                         ▼
                      Review
                         │
                         ▼
                    Final Answer
```

The core idea is simple:

> **Retrieve trusted college material first, then use the LLM to reason over that material instead of relying only on general model knowledge.**

---

## License

This project is licensed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for the complete license text.

### Important note about source documents

The MIT License applies to the project's original source code and documentation. It does **not automatically grant permission to redistribute third-party or institutional materials** stored in `data/docs/`.

For college documents:

- Keep the official source URL where available.
- Preserve attribution and source information.
- Check the original website or document for its applicable terms.
- Verify that you have permission to redistribute documents if permission is required.
- Do not assume that the project's MIT License changes the copyright or usage rights of NMAMIT/Nitte materials.

For important academic decisions, users should verify current rules, fees, deadlines, and regulations against the official institutional source.

