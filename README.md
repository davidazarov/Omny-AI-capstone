
# Omny AI
Your Elite AI Biomechanics Coach & Nutritionist.

## Overview
Omny AI is a production-ready fitness application designed to bridge the gap between generic chatbots and professional coaching. Unlike standard LLMs that often hallucinate biological data, Omny AI utilizes an agentic workflow with deterministic tools to calculate metabolic rates and macros accurately.
It solves three core user problems:

Personalization: Generates mathematical, periodized training plans based on specific biometrics.

Tracking: Uses computer vision to analyze food photos and PDF menus for hidden calories.

Accuracy: Answers general fitness questions using RAG (Retrieval-Augmented Generation) grounded in verified scientific guidelines (WHO, NSCA) rather than internet noise.

## Features

🧠 Intelligent Coach Agent: A dedicated agent that ingests user profiles (Age, Weight, Goal) to calculate BMR and Macros via function calling, delivering a downloadable 3-month text plan.

📄 PDF Plan Generation: Automatically compiles the AI's training strategy into a branded, professional PDF file for the user to download.

🥗 Calorie Vision (Multimodal): Analyzes uploaded food images or restaurant PDF menus to estimate nutritional content and recommend healthy options.

🏋️ Scientific RAG Chat: A vector-search-enabled chat interface that retrieves context from a local scientific knowledge base before answering questions.

💾 Persistent Memory: Saves user profiles and chat history to local disk (json), allowing users to return to their sessions later.

## Tech Stack

**Backend:**
Backend:

Python 3.10+
Google Gemini 2.5 Pro: Used for complex reasoning and planning.
Google Gemini 2.5 Flash: Used for low-latency multimodal (Vision) analysis.
LangChain: For orchestration and vector store management.

**Frontend:**
Streamlit: Custom UI with forced Dark Mode and persistent session state.

**Database:**
FAISS: Local vector database for RAG (Scientific Context).
JSON: Local storage for user profiles and chat history.

**AI/ML:**
Langfuse: For full-stack observability, tracing agent thoughts, latency, and tool usage.

## Architecture
Omny AI follows a modular, layered architecture to ensure separation of concerns:
UI Layer (app.py): Handles user interaction, state management, and file uploads.
Agent Layer (agent.py): distinct functions for Coach (Tools), Vision (Multimodal), and General Chat (RAG).
Tooling Layer (tools.py): Deterministic Python functions for BMR and Macro calculations.
Data Layer (ingest.py / utils.py): Handles vector ingestion, PDF generation, and file I/O.
For a detailed breakdown of technical decisions, please refer to docs/ARCHITECTURE.md.

## Installation & Setup
## Prerequisites
Python 3.10 or higher
Google AI Studio API Key
Langfuse API Keys (Public/Secret)
## Installation steps
1. Clone the repository:
git clone https://github.com/your-username/omny-ai.git
cd omny-ai
2. Install dependencies:
pip install -r requirements.txt
3. Set up environment variables: Create a .env file in the root directory:
cp .env.example .env
Populate it with your keys:
GOOGLE_API_KEY="AIzaSy..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"
4. Build the Knowledge Base (RAG): Before running the app, you must create the vector database from your PDF documents.
Place your scientific PDFs (WHO guidelines, etc.) inside the knowledge_base/ folder.
5. Run the ingestion script:
python ingest.py
Output: This will create a local faiss_index folder.

## Usage

1. Coach Plan Mode:
Go to the Sidebar and set your Profile (Age, Weight, Goal).
Click "Save Profile".
In the chat, ask: "Build me a muscle building plan."
The Agent will calculate your macros and generate a plan. Click the "Download PDF" button when it appears.

2. Calorie Vision Mode:
Switch the mode in the Sidebar to "Calorie Vision".
Upload a photo of your lunch or a PDF menu from a restaurant.
Ask: "Is this healthy?" or "What should I order?"

3. General Fitness Chat:
Switch to "General Fitness Chat".
Ask scientific questions like "What is the optimal protein intake for hypertrophy?"
The system will search your knowledge_base PDFs and cite sources.

## Deployment

**Live Application:** [https://omny-ai-bnckem4dcz8rotphws3cys.streamlit.app/]

**Deployment Platform:** Streamlit Cloud

Push your code to GitHub.

Connect your repository to Streamlit Cloud.

In the Streamlit dashboard settings, paste the contents of your .env file into the "Secrets" area.

## Project Structure

```
omny-ai/
├── app.py                  # Main Streamlit Frontend
├── agent.py                # Core Agent Logic (Coach, Vision, RAG)
├── tools.py                # Mathematical Tools (BMR, Macros)
├── utils.py                # PDF Generation & File I/O
├── ingest.py               # RAG Vector Database Builder
├── config.py               # Configuration Loader
├── prompts.py              # System Instructions & Prompts
├── requirements.txt        # Python Dependencies
├── knowledge_base/         # Folder for Scientific PDFs
├── faiss_index/            # Generated Vector Store (Local)
├── .env.example            # Environment Variable Template
├── README.md               # Project Overview
└── docs/
    ├── ARCHITECTURE.md     # Technical Decisions
    └── TOOLS.md            # Tool Documentation
```

**Note:** Component-level READMEs (e.g., `services/README.md`, `tools/README.md`) are recommended if those components need detailed explanation.

## Team

Davyd Azarov - Lead Developer & AI Engineer

Course: Data Science Capstone Project (2nd Period) Institution: NOVA IMS Year: 2025/2026
## License

[Your chosen license - MIT, Apache, etc. - not necessary]

---

## What Makes a Good README?

Your README should answer:
- **What** does this application do?
- **Why** does it exist / what problem does it solve?
- **How** do I run it locally?
- **Who** built it?

Keep it clear, organized, and professional. This is often the first thing evaluators and potential users will see.
