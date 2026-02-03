# Architecture & Technical Decisions

## 1. System Overview

Omny AI is built on a **modular, layered architecture** designed to separate the User Interface (Streamlit) from the core Agent Logic (Google Gemini). This separation ensures that the AI reasoning capabilities can be tested, iterated upon, and potentially migrated to a different frontend without rewriting the core business logic.

The application follows a **Micro-Agent pattern**, where different "modes" (Coach, Vision, General Chat) utilize different model configurations and tools suited to their specific tasks.

---

## 2. Architectural Layers

### A. Presentation Layer (Frontend)
* **Technology:** Streamlit
* **Role:** Handles user input, state management, and data visualization.
* **Key Decision - Persistent Session State:** We utilize `st.session_state` combined with local JSON storage (`utils.py`). This allows the application to "remember" the user's conversation and profile data even if the browser is refreshed, mimicking a production-grade database interaction without the overhead of setting up SQL/NoSQL for an MVP.
* **UX Design:** Custom CSS injection is used to enforce a "Dark Mode" aesthetic, ensuring a professional look that aligns with modern fitness apps.

### B. Logic Layer (The Agent)
* **Technology:** Google Generative AI SDK (`google-generativeai`)
* **Role:** Orchestrates the reasoning, tool selection, and response generation.
* **Hybrid Model Strategy:** We deliberately employ a multi-model approach to balance intelligence vs. latency:
    1.  **Gemini 2.5 Pro:** Used for the **Coach Agent** and **General Chat**.
        * *Justification:* These tasks require complex instruction following (following the JSON schema for plans) and deep reasoning (connecting scientific context to user queries).
    2.  **Gemini 2.5 Flash:** Used for **Calorie Vision**.
        * *Justification:* "Flash" models are optimized for high-volume, low-latency tasks. For analyzing images and extracting text from PDF menus, speed is critical for a good user experience.

### C. Tooling Layer (Deterministic Execution)
* **Technology:** Native Python Functions (`tools.py`)
* **Role:** Performs mathematical calculations.
* **Key Decision - Deterministic vs. Probabilistic:** LLMs are excellent at strategy but notoriously poor at arithmetic. To prevent "hallucinations" (e.g., calculating a BMR of 5000 incorrectly), we offload all math to deterministic Python functions (`calculate_bmr`, `calculate_macros`). The Agent is strictly forbidden from doing math itself; it must call the tools.

### D. Data Layer (RAG & Storage)
* **Technology:** FAISS (Vector Store) & Local JSON
* **Role:** Stores scientific context and user data.
* **Retrieval-Augmented Generation (RAG):**
    * **Vector Store:** We chose **FAISS (Facebook AI Similarity Search)** running locally over a cloud-based solution (like Pinecone).
    * *Justification:* Since our "Knowledge Base" consists of a fixed set of verified guidelines (WHO, NSCA PDFs) that do not change frequently, a local index is significantly faster (zero network latency for retrieval) and simplifies deployment (no external vector DB credentials required).
    * **Embeddings:** `GoogleGenerativeAIEmbeddings` (`models/embedding-001`) are used to ensure the vector space is semantically aligned with the Gemini generation model.

---

## 3. Technical Choices & Justifications

### Why Google Gemini over OpenAI?
While OpenAI is a standard, we selected Google Gemini for three specific advantages in this use case:
1.  **Native Multimodality:** Gemini was built from the ground up to handle video and images. The **Calorie Vision** feature relies on this native capability to analyze food photos without needing a separate OCR pipeline (like Tesseract).
2.  **Context Window:** The large context window allows us to ingest entire PDF menus or lengthy conversation histories without aggressive truncation.
3.  **Cost Efficiency:** The free tier availability allows for extensive testing of the "Pro" models without incurring significant development costs.

### Why Langfuse for Observability?
To meet the requirement for "AI Observability," we integrated **Langfuse**.
* **Implementation:** We use the **Decorator Pattern** (`@observe()`) in `agent.py`.
* **Benefit:** This provides granular "X-Ray" vision into the application. We can see exactly when the model decided to call a tool, what arguments it passed (e.g., `weight=75`), and if it failed. This is critical for debugging "Silent Failures" where the model gives a polite but wrong answer.

### Why FPDF for Document Generation?
The Coach Agent generates a text-based plan, but users expect a tangible takeaway.
* **Solution:** We implemented a post-processing pipeline in `utils.py` using `fpdf`.
* **Justification:** Instead of asking the LLM to generate code (which is error-prone), we take the *structured text output* of the LLM and pass it through a rigid Python formatter. This ensures the final PDF always has the correct logo, headers, and formatting, regardless of minor variations in the AI's text output.

---

## 4. Data Flow Diagram

1.  **User Input** (Streamlit)
    ⬇
2.  **Profile Injection** (System Prompt augments query with Age/Weight/Goal)
    ⬇
3.  **Agent Decision** (Gemini 2.5 Pro)
    * *Path A (Need Math):* Call `tools.calculate_macros` ➡ Return Result ➡ Generate Text.
    * *Path B (Need Science):* Query FAISS ➡ Retrieve Chunks ➡ Augment Prompt ➡ Generate Answer.
    * *Path C (Vision):* Send Image Bytes to Gemini Flash ➡ Analyze ➡ Return Description.
    ⬇
4.  **Response Handling**
    * Text displayed in Chat.
    * If "Plan" detected ➡ `utils.create_pdf()` generates binary.
    ⬇
5.  **Observability** (Langfuse)
    * Trace sent asynchronously to cloud for monitoring.