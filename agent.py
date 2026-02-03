from langfuse.langchain import CallbackHandler
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langfuse import observe
import config
import tools
import prompts

# Configure Gemini once
genai.configure(api_key=config.GOOGLE_API_KEY)

# Define Safety Settings Globaly
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

@observe()
def get_coach_response(user_input, chat_history, user_profile):
    """
    Handles the Coach Logic.
    Args:
        user_input (str): The user's message.
        chat_history (list): List of previous messages in Gemini format.
        user_profile (dict): Dictionary containing age, weight, height, goal, gender.
    """
    # 1. Setup Tools
    # Note: Removed YouTube tool as per your request to focus on text
    my_tools = [tools.calculate_bmr, tools.calculate_macros]

    # 2. Inject Profile Data into Prompt
    dynamic_instruction = prompts.COACH_SYSTEM_PROMPT + f"""
    
    ACTIVE USER PROFILE:
    - Age: {user_profile['age']}
    - Weight: {user_profile['weight']}kg
    - Height: {user_profile['height']}cm
    - Gender: {user_profile['gender']}
    - Goal: {user_profile['goal']}
    
    INSTRUCTION: Focus purely on writing the detailed text plan. Do not search for videos.
    """

    # 3. Initialize Model
    model = genai.GenerativeModel(
        model_name=config.MODEL_NAME, 
        system_instruction=dynamic_instruction,
        tools=my_tools 
    )

    # 4. Start Chat
    chat = model.start_chat(history=chat_history, enable_automatic_function_calling=True)
    
    # 5. Send Message
    response = chat.send_message(user_input, safety_settings=SAFETY_SETTINGS)
    return response.text


def get_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # Allow dangerous deserialization is required for local files created by us
    return FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

@observe()
def get_general_response(user_input, chat_history):
    """
    Handles the General Fitness Chat Logic with RAG (Scientific Search).
    """
    context_text = ""
    
    # 1. Search the Vector Database
    try:
        vector_db = get_vector_store()
        # Search for the 3 most relevant chunks
        results = vector_db.similarity_search(user_input, k=3)
        
        # Combine them into a single string
        context_text = "\n\n".join([doc.page_content for doc in results])
        print(f"✅ Found {len(results)} relevant scientific chunks.") # For debugging
    except Exception as e:
        print(f"⚠️ Vector Search skipped: {e}")
        # Use fallback if DB isn't ready
        context_text = "No specific scientific context available."

    # 2. Construct the RAG Prompt
    # We combine the System Instructions + The Found Context
    rag_instruction = prompts.RAG_SYSTEM_PROMPT + f"""
    
    📚 SCIENTIFIC CONTEXT FOUND:
    {context_text}
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=rag_instruction
    )
    
    # 3. Generate Answer
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(user_input, safety_settings=SAFETY_SETTINGS)
    return response.text


@observe()
def analyze_document(file_data, user_text, is_pdf=False):
    """
    Handles Image and PDF analysis.
    Args:
        file_data (dict): The processed file dictionary from utils.
        user_text (str): The user's question.
        is_pdf (bool): True if PDF, False if Image.
    """
    vision_model = genai.GenerativeModel("gemini-2.5-flash")
    
    request_content = []
    
    # 1. Select Prompt based on file type
    if is_pdf:
        base_prompt = prompts.VISION_PDF_PROMPT
    else:
        base_prompt = prompts.VISION_IMAGE_PROMPT
        
    # 2. Add User Context
    if user_text:
        base_prompt += f"\n\nUSER QUESTION/CONTEXT: '{user_text}'"
    
    request_content.append(base_prompt)
    
    # 3. Add File Data
    if file_data:
        request_content.append(file_data)
        
    # 4. Generate
    response = vision_model.generate_content(request_content)
    return response.text