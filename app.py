import streamlit as st
import config
import utils
import agent

# ---------------------------------------------------------
# 1. DESIGN & CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Omny AI",
    page_icon="Omny logo main 2.png",
    layout="wide"
)

# Force Black Theme & White Text
def load_css():
    st.markdown("""
        <style>
        /* General Text Color */
        h1, h2, h3, h4, h5, h6, p, label, span, div { color: #FFFFFF !important; }
        
        /* Backgrounds */
        .stApp { background-color: #000000 !important; }
        [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #333333; }
        
        /* Inputs */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox, div[data-baseweb="select"] {
            background-color: #111111 !important; 
            color: #FFFFFF !important;
            border: 1px solid #333333 !important;
        }
        
        /* ROUNDED LOGO IMPLEMENTATION */
        [data-testid="stSidebar"] img {
            border-radius: 50%;
            object-fit: cover;
        }
        
        /* Chat Avatar Styling */
        .stChatMessage .stImage {
            border-radius: 50% !important;
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------
# 2. SIDEBAR & NAVIGATION (With Persistence)
# ---------------------------------------------------------
st.logo("Omny logo main 2.png", icon_image="Omny logo main 2.png")

with st.sidebar:
    st.image("Omny logo main.png", width=150)
    st.markdown("---")
    
    mode = st.radio("Select Mode:", ["🧠 Coach Plan", "🥗 Calorie Vision", "🏋️ General Fitness Chat"])
    
    st.markdown("---")
    st.header("Your Profile")
    
    # 1. Load saved data from disk
    saved_data = utils.load_profile()
    
    # 2. Initialize Session State (Use saved data if it exists, otherwise use defaults)
    if "age" not in st.session_state: 
        st.session_state.age = saved_data["age"] if saved_data else 25
        
    if "weight" not in st.session_state: 
        st.session_state.weight = saved_data["weight"] if saved_data else 75.0
        
    if "height" not in st.session_state:
        st.session_state.height = saved_data["height"] if saved_data else 175
        
    if "gender" not in st.session_state:
        # Note: Selectbox needs an index (0 for Male, 1 for Female)
        saved_gender = saved_data.get("gender", "Male") if saved_data else "Male"
        st.session_state.gender_index = 0 if saved_gender == "Male" else 1

    if "goal" not in st.session_state:
        # Map goal string to index
        saved_goal = saved_data.get("goal", "Lose Fat") if saved_data else "Lose Fat"
        goals = ["Lose Fat", "Build Muscle", "Maintain"]
        st.session_state.goal_index = goals.index(saved_goal) if saved_goal in goals else 0

    # 3. Render Widgets (Linked to Session State)
    age = st.number_input("Age", 16, 90, key="age")
    weight = st.number_input("Weight (kg)", 40.0, 200.0, key="weight")
    height = st.number_input("Height (cm)", 120, 220, key="height")
    
    gender = st.selectbox("Gender", ["Male", "Female"], index=st.session_state.get("gender_index", 0))
    goal = st.selectbox("Goal", ["Lose Fat", "Build Muscle", "Maintain"], index=st.session_state.get("goal_index", 0))

    # 4. Save Button
    if st.button("💾 Save Profile"):
        # Create a clean dictionary to save
        profile_data = {
            "age": age,
            "weight": weight,
            "height": height,
            "gender": gender,
            "goal": goal
        }
        # Call the tool
        if utils.save_profile(profile_data):
            st.success("✅ Profile Saved!")
        else:
            st.error("❌ Save Failed.")
    

    st.markdown("---") # Visual separator
    # NEW: Reset Chat Button
    if st.button("🗑️ Reset Chat History"):
        # 1. Delete the file
        utils.clear_chat_history()
        
        # 2. Clear the memory
        if "coach_messages" in st.session_state:
            del st.session_state["coach_messages"]
        if "general_messages" in st.session_state:
            del st.session_state["general_messages"]
            
        # 3. Refresh the app to restart
        st.rerun()

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_gemini_history(session_key):
    """
    Converts Streamlit session history into Gemini API format.
    Accepts 'coach_messages' or 'general_messages' as input.
    """
    gemini_history = []
    if session_key in st.session_state:
        for msg in st.session_state[session_key]:
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
    return gemini_history

# ---------------------------------------------------------
# 4. INITIALIZE HISTORY (Load from File)
# ---------------------------------------------------------
# Load history ONCE when the script runs
saved_chats = utils.load_chat_history()

# Coach History
if "coach_messages" not in st.session_state:
    if saved_chats and "coach_messages" in saved_chats:
        st.session_state.coach_messages = saved_chats["coach_messages"]
    else:
        st.session_state.coach_messages = [
            {"role": "assistant", "content": "Hello! I am Omny AI. Ready to build your plan?"}
        ]

# General Chat History
if "general_messages" not in st.session_state:
    if saved_chats and "general_messages" in saved_chats:
        st.session_state.general_messages = saved_chats["general_messages"]
    else:
        st.session_state.general_messages = [
            {"role": "assistant", "content": "Ask me anything about training, diet, or sleep."}
        ]

# ---------------------------------------------------------
# 5. MAIN APP LOGIC
# ---------------------------------------------------------

# === MODE 1: COACH PLAN ===
if mode == "🧠 Coach Plan":
    st.title("🧠 Omny AI Coach")
    st.caption("Detailed Training & Diet Planning")

    # Display Chat
    for message in st.session_state.coach_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle Input
    if prompt := st.chat_input("Ask for a plan..."):
        with st.chat_message("user", avatar="User.png"):
            st.markdown(prompt)
        st.session_state.coach_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="Omny logo main 2.png"):
            with st.spinner("Analyzing..."):
                try:
                    # Collect Profile Data
                    user_profile = {
                        "age": age, "weight": weight, "height": height, 
                        "gender": gender, "goal": goal
                    }
                    
                    # Get History
                    history = get_gemini_history("coach_messages")
                    
                    # CALL AGENT
                    reply = agent.get_coach_response(prompt, history, user_profile)
                    
                    st.markdown(reply)
                    st.session_state.coach_messages.append({"role": "assistant", "content": reply})

                    # === Auto-Save Chat ===
                    utils.save_chat_history(
                        st.session_state.coach_messages, 
                        st.session_state.general_messages
                    )

                
                    # === Download Plan Button (PDF Version) ===
                    if "Week 1" in reply or "Month 1" in reply:
                        # Generate PDF bytes
                        pdf_data = utils.create_pdf(reply)
                        
                        st.download_button(
                            label="📄 Download Plan as PDF",
                            data=pdf_data,
                            file_name="Omny_Fitness_Plan.pdf",
                            mime="application/pdf"
                        )

                except Exception as e:
                    st.error(f"Error: {e}")

# === MODE 2: CALORIE VISION ===
elif mode == "🥗 Calorie Vision":
    st.title("🥗 Food & Menu Scanner")
    st.write("Upload a food photo OR a PDF Menu.")

    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_file = st.file_uploader("Upload File", type=["jpg", "jpeg", "png", "pdf"])
        if uploaded_file:
            if uploaded_file.type == "application/pdf": st.info("📄 PDF Menu Uploaded")
            else: st.image(uploaded_file, width=250)
    with col2:
        food_text = st.text_area("Description / Question", height=150)

    if st.button("Analyze File"):
        if not uploaded_file and not food_text:
            st.warning("Please upload a file or ask a question.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    # Process file using utils
                    file_data = utils.process_file(uploaded_file)
                    is_pdf = (uploaded_file.type == "application/pdf") if uploaded_file else False
                    
                    # CALL AGENT
                    reply = agent.analyze_document(file_data, food_text, is_pdf)
                    st.markdown(reply)
                except Exception as e:
                    st.error(f"Error: {e}")

# === MODE 3: GENERAL CHAT ===
elif mode == "🏋️ General Fitness Chat":
    st.title("🏋️ General Fitness Chat")

    for message in st.session_state.general_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question..."):
        with st.chat_message("user", avatar="User.png"):
            st.markdown(prompt)
        st.session_state.general_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="Omny logo main 2.png"):
            with st.spinner("Thinking..."):
                try:
                    # Get History
                    history = get_gemini_history("general_messages")
                    
                    # CALL AGENT (With RAG)
                    reply = agent.get_general_response(prompt, history)
                    
                    st.markdown(reply)
                    st.session_state.general_messages.append({"role": "assistant", "content": reply})

                    # === Auto-Save Chat ===
                    utils.save_chat_history(
                        st.session_state.coach_messages, 
                        st.session_state.general_messages
                    )

                except Exception as e:
                    st.error(f"Error: {e}")