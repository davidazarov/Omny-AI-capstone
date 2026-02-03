import base64
import json
import os
import re
from fpdf import FPDF

# ==========================================
# 1. FILE PROCESSING (Keep this for Vision Mode!)
# ==========================================
def process_file(uploaded_file):
    """
    Converts a Streamlit file upload (Image OR PDF) into the format Gemini needs.
    """
    if uploaded_file is not None:
        # Read the file bytes
        bytes_data = uploaded_file.getvalue()
        
        # Get the correct mime type (image/jpeg, application/pdf, etc.)
        mime_type = uploaded_file.type
        
        # Return the dictionary format required by Google GenAI
        return {"mime_type": mime_type, "data": bytes_data}
    return None

# ==========================================
# 2. DATA MANAGEMENT (Save/Load/Clear)
# ==========================================
PROFILE_FILE = "user_profile.json"
CHAT_FILE = "chat_history.json"

def save_profile(profile_data):
    """Saves user settings to a local JSON file."""
    try:
        with open(PROFILE_FILE, "w") as f:
            json.dump(profile_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False

def load_profile():
    """Reads the user profile from disk."""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading profile: {e}")
    return None

def save_chat_history(coach_msgs, general_msgs):
    """Saves chat history to disk."""
    data = {
        "coach_messages": coach_msgs,
        "general_messages": general_msgs
    }
    try:
        with open(CHAT_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_chat_history():
    """Loads chat history from disk."""
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")
    return None

def clear_chat_history():
    """Deletes the chat history file."""
    if os.path.exists(CHAT_FILE):
        try:
            os.remove(CHAT_FILE)
            return True
        except Exception as e:
            print(f"Error clearing chat file: {e}")
            return False
    return True

# ==========================================
# 3. PDF GENERATION (Clean & Branded)
# ==========================================

class BrandedPDF(FPDF):
    def header(self):
        # 1. Add Logo to top left
        # Ensure 'Omny logo main 2.png' is in your project folder
        try:
            self.image('Omny logo main 2.png', 10, 8, 25)
        except:
            pass # Skip if image not found

        # 2. Add Title to the right of the logo
        self.set_font('Arial', 'B', 15)
        self.cell(80) # Move cursor to the right
        self.cell(30, 10, 'Omny AI Fitness Plan', 0, 0, 'C')
        
        # 3. Line break to separate header from body
        self.ln(25)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def clean_markdown(text):
    """
    Removes Markdown symbols to make text look like a clean document.
    """
    # 1. Remove Headers (### Title -> Title)
    text = re.sub(r'#+\s?', '', text)
    
    # 2. Remove Bold (**Text** -> Text)
    text = text.replace('**', '')
    
    # 3. Remove Italic/Bullets (* -> empty)
    text = text.replace('*', '') 
    
    # 4. Fix double spaces caused by removal
    text = text.replace('  ', ' ')
    
    return text

def create_pdf(raw_text):
    """
    Generates a PDF file from text, cleaning formatting first.
    """
    pdf = BrandedPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Process text line by line to handle formatting nicely
    lines = raw_text.split('\n')
    
    for line in lines:
        clean_line = clean_markdown(line).strip()
        
        if not clean_line:
            pdf.ln(5) # Add small space for empty lines
            continue
            
        # Detect Titles (capitalized short lines, or lines that used to have ###)
        if "###" in line or (len(clean_line) < 50 and clean_line.isupper() and len(clean_line) > 3):
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, clean_line, ln=True)
            pdf.set_font("Arial", "", 12) # Reset to normal
            
        # Detect Data Lines (Label: Value) to simulate a table look
        elif ":" in clean_line and len(clean_line) < 80:
            parts = clean_line.split(":", 1)
            
            # Bold Label (Left side)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(90, 8, parts[0] + ":", ln=0)
            
            # Normal Value (Right side)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, parts[1], ln=True)
            
        # Normal Text
        else:
            pdf.set_font("Arial", size=12)
            # Encode latin-1 to handle special characters
            clean_line = clean_line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 8, txt=clean_line)
            
    # Return as bytes
    return pdf.output(dest="S").encode("latin-1")