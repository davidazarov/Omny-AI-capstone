import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def create_vector_db():
    print("🔄 Loading PDFs from 'knowledge_base' folder...")
    
    # 1. Load PDFs
    loader = PyPDFDirectoryLoader("knowledge_base")
    documents = loader.load()
    
    if not documents:
        print("❌ No PDFs found! Please add files to 'knowledge_base/'.")
        return

    print(f"✅ Loaded {len(documents)} document pages.")

    # 2. Split Text into Chunks (bite-sized pieces for the AI)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"🧩 Split into {len(chunks)} text chunks.")

    # 3. Create Embeddings & Vector Store
    print("🔮 Generating Embeddings (this may take a moment)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    vector_store = FAISS.from_documents(chunks, embeddings)

    # 4. Save to Disk
    vector_store.save_local("faiss_index")
    print("💾 Success! Vector Database saved to 'faiss_index' folder.")

if __name__ == "__main__":
    create_vector_db()