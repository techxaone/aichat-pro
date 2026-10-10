"""
AIChat Pro — Smart AI Chatbot with Groq & RAG (FREE)
Author: Techxaone
"""

import streamlit as st
import os
from datetime import datetime

from config import config
from chatbot import Chatbot
from rag_engine import RAGEngine


# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AIChat Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #64748b;
        font-size: 1rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    .user-message {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background: #f1f5f9;
        color: #0f172a;
        margin-right: 20%;
        border-left: 3px solid #6366f1;
    }
    .source-card {
        background: #fef3c7;
        border-left: 3px solid #f59e0b;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    [data-testid="stSidebar"] {
        background: #f8fafc;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ==================== INIT SESSION ====================
def init_session():
    """Initialize session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = Chatbot()
        except Exception as e:
            st.error(f"❌ Failed to initialize chatbot: {e}")
            st.stop()
    
    if "rag" not in st.session_state:
        try:
            st.session_state.rag = RAGEngine()
        except Exception as e:
            st.session_state.rag = None
    
    if "mode" not in st.session_state:
        st.session_state.mode = "💬 Chat"
    
    if "rag_ready" not in st.session_state:
        st.session_state.rag_ready = False


init_session()


# ==================== API KEY CHECK ====================
if not config.is_valid():
    st.markdown('<h1 class="main-header">🤖 AIChat Pro</h1>', unsafe_allow_html=True)
    st.error("### 🔑 Groq API Key Required (FREE)")
    
    st.markdown(
        "**Setup Steps:**\n\n"
        "1. Create a `.env` file in the project root\n"
        "2. Add your Groq API key: `GROQ_API_KEY=gsk-your-key-here`\n"
        "3. Get your **FREE** key from: [console.groq.com/keys](https://console.groq.com/keys)\n"
        "4. Restart the app"
    )
    
    with st.expander("📝 Or set it here (temporary)"):
        temp_key = st.text_input("Groq API Key", type="password")
        if st.button("Save & Reload"):
            os.environ["GROQ_API_KEY"] = temp_key
            st.rerun()
    
    st.stop()


# ==================== HEADER ====================
st.markdown('<h1 class="main-header">🤖 AIChat Pro</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Smart AI Chatbot · Groq · RAG · Chat with Documents (FREE)</p>',
    unsafe_allow_html=True
)


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    mode = st.radio(
        "**Mode**",
        ["💬 Chat", "📄 Chat with Documents"],
        index=0 if st.session_state.mode == "💬 Chat" else 1
    )
    st.session_state.mode = mode
    
    st.markdown("---")
    
    # ============ CHAT MODE ============
    if mode == "💬 Chat":
        st.markdown("### 🎭 AI Personality")
        
        personality = st.selectbox(
            "Choose AI personality",
            [
                "Default Assistant",
                "Python Expert",
                "Data Scientist",
                "Business Consultant",
                "Teacher / Explainer",
                "Creative Writer",
                "Code Reviewer",
                "Custom",
            ]
        )
        
        personalities = {
            "Default Assistant": (
                "You are AIChat Pro, a helpful, friendly, and intelligent AI assistant. "
                "You provide clear, accurate, and detailed responses."
            ),
            "Python Expert": (
                "You are an expert Python developer with 15+ years of experience. "
                "You write clean, efficient, and well-documented code. "
                "You explain advanced concepts simply."
            ),
            "Data Scientist": (
                "You are a senior data scientist specializing in ML, statistics, and analytics. "
                "You provide data-driven insights and explain complex concepts clearly."
            ),
            "Business Consultant": (
                "You are a strategic business consultant. "
                "You provide actionable advice, focus on ROI, and think practically."
            ),
            "Teacher / Explainer": (
                "You are a patient teacher. You break down complex topics into simple explanations "
                "with examples, analogies, and step-by-step guides."
            ),
            "Creative Writer": (
                "You are a creative writer with a flair for storytelling. "
                "You write engaging, vivid, and memorable content."
            ),
            "Code Reviewer": (
                "You are a senior code reviewer. You analyze code for bugs, performance, "
                "security, and best practices. You suggest improvements constructively."
            ),
            "Custom": "",
        }
        
        if personality == "Custom":
            system_prompt = st.text_area(
                "Custom system prompt",
                height=100,
                placeholder="You are..."
            )
        else:
            system_prompt = personalities[personality]
            st.caption(f"*{personality}*")
        
        if st.button("✅ Apply Personality", use_container_width=True):
            if system_prompt:
                st.session_state.chatbot.set_system_prompt(system_prompt)
                st.success("Personality updated!")
    
    # ============ RAG MODE ============
    else:
        st.markdown("### 📄 Upload Documents")
        st.caption("Supported: PDF, TXT, MD")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            if st.button("📚 Process Documents", use_container_width=True, type="primary"):
                with st.spinner("Processing documents..."):
                    try:
                        saved_paths = []
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(config.DOCS_DIR, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            saved_paths.append(file_path)
                        
                        num_chunks = st.session_state.rag.load_documents(saved_paths)
                        st.session_state.rag_ready = True
                        
                        st.success(f"✅ Processed {len(uploaded_files)} file(s) → {num_chunks} chunks")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        if not st.session_state.rag_ready and st.session_state.rag:
            if st.session_state.rag.load_existing():
                st.session_state.rag_ready = True
                st.info("📚 Loaded existing document index")
        
        if st.session_state.rag_ready:
            st.success("✅ Documents ready for Q&A")
            
            if st.button("🗑️ Clear Documents", use_container_width=True):
                st.session_state.rag.clear()
                st.session_state.rag_ready = False
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎮 Controls")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chatbot.clear_history()
            if st.session_state.rag:
                st.session_state.rag.memory.clear()
            st.rerun()
    
    with col_b:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chatbot.clear_history()
            if st.session_state.rag:
                st.session_state.rag.clear()
            st.session_state.rag_ready = False
            st.rerun()
    
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 📥 Export")
        
        chat_md = st.session_state.chatbot.export_chat()
        st.download_button(
            "Download Chat (.md)",
            chat_md,
            file_name=f"aichat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    st.markdown("---")
    st.markdown(
        f"<center><small>AIChat Pro v{config.APP_VERSION}<br>Powered by Groq (FREE)</small></center>",
        unsafe_allow_html=True
    )


# ==================== MAIN CHAT AREA ====================
st.markdown(f"### {st.session_state.mode}")

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'<div class="chat-message user-message">{message["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-message assistant-message">{message["content"]}</div>',
            unsafe_allow_html=True
        )
        
        if "sources" in message and message["sources"]:
            with st.expander(f"📚 Sources ({len(message['sources'])})"):
                for i, src in enumerate(message["sources"], 1):
                    st.markdown(
                        f'<div class="source-card"><b>Source {i}:</b> '
                        f'{os.path.basename(src["source"])} (Page {src["page"]})'
                        f'<br><small>{src["content"]}</small></div>',
                        unsafe_allow_html=True
                    )


# ==================== INPUT ====================
if st.session_state.mode == "💬 Chat":
    prompt = st.chat_input("Type your message...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(
            f'<div class="chat-message user-message">{prompt}</div>',
            unsafe_allow_html=True
        )
        
        with st.spinner("🤔 Thinking..."):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                for chunk in st.session_state.chatbot.stream_chat(prompt):
                    full_response += chunk
                    response_placeholder.markdown(
                        f'<div class="chat-message assistant-message">{full_response}▌</div>',
                        unsafe_allow_html=True
                    )
                
                response_placeholder.markdown(
                    f'<div class="chat-message assistant-message">{full_response}</div>',
                    unsafe_allow_html=True
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                })
            except Exception as e:
                st.error(f"❌ Error: {e}")

else:
    if not st.session_state.rag_ready:
        st.info("👈 Please upload and process documents first.")
    else:
        prompt = st.chat_input("Ask a question about your documents...")
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.markdown(
                f'<div class="chat-message user-message">{prompt}</div>',
                unsafe_allow_html=True
            )
            
            with st.spinner("🔍 Searching documents..."):
                try:
                    result = st.session_state.rag.query(prompt)
                    
                    st.markdown(
                        f'<div class="chat-message assistant-message">{result["answer"]}</div>',
                        unsafe_allow_html=True
                    )
                    
                    if result["sources"]:
                        with st.expander(f"📚 Sources ({len(result['sources'])})", expanded=True):
                            for i, src in enumerate(result["sources"], 1):
                                st.markdown(
                                    f'<div class="source-card"><b>Source {i}:</b> '
                                    f'{os.path.basename(src["source"])} (Page {src["page"]})'
                                    f'<br><small>{src["content"]}</small></div>',
                                    unsafe_allow_html=True
                                )
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    })
                except Exception as e:
                    st.error(f"❌ Error: {e}")


# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #94a3b8;'>Built with ❤️ by "
    "<b>Techxaone</b> — AI & Machine Learning Solutions</p>",
    unsafe_allow_html=True
)