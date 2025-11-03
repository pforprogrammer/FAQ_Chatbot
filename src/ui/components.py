"""
Streamlit UI Components
Reusable UI components for the chatbot interface
"""
import streamlit as st
from typing import Optional, List
import time

from src.services.chatbot import Chatbot, ChatbotResponse
from src.models.faq import FAQCategory, ChatMessage
from src.config import config


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    # Initialize chatbot
    if config.SESSION_CHATBOT not in st.session_state:
        with st.spinner("🤖 Initializing chatbot..."):
            try:
                st.session_state[config.SESSION_CHATBOT] = Chatbot()
            except Exception as e:
                st.error(f"❌ Error initializing chatbot: {e}")
                st.stop()
    
    # Initialize messages
    if config.SESSION_MESSAGES not in st.session_state:
        st.session_state[config.SESSION_MESSAGES] = []
        # Add welcome message
        welcome_msg = (
            "👋 **Welcome to CodeAlpha FAQ Chatbot!**\n\n"
            "I'm here to help answer your questions about CodeAlpha internships. "
            "Feel free to ask me anything!\n\n"
            "💡 **Try asking:**\n"
            "- What is CodeAlpha?\n"
            "- How do I apply for the internship?\n"
            "- What are the task requirements?"
        )
        st.session_state[config.SESSION_MESSAGES].append({
            "role": "assistant",
            "content": welcome_msg,
            "match_result": None
        })


def apply_custom_styles() -> None:
    """Apply custom CSS styles to the Streamlit app."""
    st.markdown("""
        <style>
        /* Main container */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header-title {
            color: white;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0;
            text-align: center;
        }
        
        .header-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            text-align: center;
            margin-top: 0.5rem;
        }
        
        /* Chat message styling */
        .chat-message {
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .chat-message.user {
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
        }
        
        .chat-message.assistant {
            background-color: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        
        .message-role {
            font-weight: bold;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
        }
        
        .message-role.user {
            color: #1976D2;
        }
        
        .message-role.assistant {
            color: #7b1fa2;
        }
        
        /* Confidence badge */
        .confidence-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            margin-top: 0.5rem;
        }
        
        .confidence-high {
            background-color: #4caf50;
            color: white;
        }
        
        .confidence-medium {
            background-color: #ff9800;
            color: white;
        }
        
        .confidence-low {
            background-color: #f44336;
            color: white;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: white;
        }
        
        /* Category badge */
        .category-badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.8rem;
            background-color: #e0e0e0;
            color: #424242;
            margin-left: 0.5rem;
        }
        
        /* Statistics card */
        .stat-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.2rem;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f5f5f5;
            border-radius: 8px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        </style>
    """, unsafe_allow_html=True)


def render_header() -> None:
    """Render the application header."""
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">🤖 CodeAlpha FAQ Chatbot</h1>
            <p class="header-subtitle">
                Your AI-powered assistant for CodeAlpha internship queries
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_chat_message(message: dict) -> None:
    """
    Render a single chat message.
    
    Args:
        message: Message dictionary with role, content, and optional match_result
    """
    role = message["role"]
    content = message["content"]
    match_result = message.get("match_result")
    
    # Message container
    role_class = "user" if role == "user" else "assistant"
    role_icon = "👤" if role == "user" else "🤖"
    role_label = "You" if role == "user" else "Assistant"
    
    st.markdown(f"""
        <div class="chat-message {role_class}">
            <div class="message-role {role_class}">{role_icon} {role_label}</div>
            <div class="message-content">
    """, unsafe_allow_html=True)
    
    # Message content
    st.markdown(content)
    
    # Show confidence badge for assistant messages with matches
    if role == "assistant" and match_result:
        confidence = match_result.confidence_percentage
        confidence_level = match_result.confidence_level.lower()
        
        st.markdown(f"""
            <span class="confidence-badge confidence-{confidence_level}">
                {confidence}% Confident
            </span>
            <span class="category-badge">
                {match_result.faq.category.value.capitalize()}
            </span>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_chat_interface() -> None:
    """Render the main chat interface."""
    chatbot: Chatbot = st.session_state[config.SESSION_CHATBOT]
    messages: List[dict] = st.session_state[config.SESSION_MESSAGES]
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        # Display all messages
        for message in messages:
            render_chat_message(message)
    
    # Chat input at the bottom
    st.markdown("---")
    
    # User input
    user_input = st.chat_input(
        "Ask me anything about CodeAlpha internships...",
        key="user_input"
    )
    
    if user_input:
        # Add user message to display
        st.session_state[config.SESSION_MESSAGES].append({
            "role": "user",
            "content": user_input,
            "match_result": None
        })
        
        # Get chatbot response
        with st.spinner("🤔 Thinking..."):
            response = chatbot.ask(user_input)
        
        # Add assistant response to display
        st.session_state[config.SESSION_MESSAGES].append({
            "role": "assistant",
            "content": response.message,
            "match_result": response.match_result
        })
        
        # Rerun to update display
        st.rerun()


def render_sidebar() -> None:
    """Render the sidebar with additional features."""
    chatbot: Chatbot = st.session_state[config.SESSION_CHATBOT]
    
    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state[config.SESSION_MESSAGES] = []
            chatbot.clear_history()
            st.rerun()
        
        st.markdown("---")
        
        # Statistics section
        st.markdown("### 📊 Statistics")
        stats = chatbot.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{stats['total_faqs']}</div>
                    <div class="stat-label">Total FAQs</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{stats['conversation_turns']}</div>
                    <div class="stat-label">Messages</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Category browser
        render_category_browser(chatbot)
        
        st.markdown("---")
        
        # Keyword search
        render_keyword_search(chatbot)
        
        st.markdown("---")
        
        # Quick suggestions
        render_quick_suggestions(chatbot)
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
                **CodeAlpha FAQ Chatbot**
                
                Version 1.0.0
                
                Built with:
                - Python 3.11+
                - Streamlit
                - NLTK
                - scikit-learn
                
                Features:
                - Natural Language Processing
                - Intelligent Question Matching
                - Conversation History
                - Category Browsing
                - Keyword Search
                
                📧 Contact: services@codealpha.tech
            """)


def render_category_browser(chatbot: Chatbot) -> None:
    """Render category browser in sidebar."""
    st.markdown("### 📁 Browse by Category")
    
    categories = chatbot.get_all_categories()
    
    for category in categories:
        faqs = chatbot.get_faqs_by_category(category)
        
        with st.expander(f"{category.value.capitalize()} ({len(faqs)})"):
            for faq in faqs:
                if st.button(
                    f"💬 {faq.question[:50]}...",
                    key=f"cat_{faq.id}",
                    use_container_width=True
                ):
                    # Add FAQ question as user input
                    st.session_state[config.SESSION_MESSAGES].append({
                        "role": "user",
                        "content": faq.question,
                        "match_result": None
                    })
                    
                    # Get response
                    response = chatbot.ask(faq.question)
                    
                    st.session_state[config.SESSION_MESSAGES].append({
                        "role": "assistant",
                        "content": response.message,
                        "match_result": response.match_result
                    })
                    
                    st.rerun()


def render_keyword_search(chatbot: Chatbot) -> None:
    """Render keyword search in sidebar."""
    st.markdown("### 🔍 Search by Keyword")
    
    search_term = st.text_input(
        "Enter keyword",
        placeholder="e.g., python, certificate",
        key="keyword_search"
    )
    
    if search_term:
        results = chatbot.search_by_keyword(search_term)
        
        if results:
            st.success(f"Found {len(results)} FAQ(s)")
            
            for faq in results[:5]:  # Show top 5
                if st.button(
                    f"💬 {faq.question[:45]}...",
                    key=f"search_{faq.id}",
                    use_container_width=True
                ):
                    # Add FAQ question as user input
                    st.session_state[config.SESSION_MESSAGES].append({
                        "role": "user",
                        "content": faq.question,
                        "match_result": None
                    })
                    
                    # Get response
                    response = chatbot.ask(faq.question)
                    
                    st.session_state[config.SESSION_MESSAGES].append({
                        "role": "assistant",
                        "content": response.message,
                        "match_result": response.match_result
                    })
                    
                    st.rerun()
        else:
            st.info("No results found")


def render_quick_suggestions(chatbot: Chatbot) -> None:
    """Render quick suggestion buttons."""
    st.markdown("### 💡 Quick Questions")
    
    suggestions = [
        "What is CodeAlpha?",
        "How to apply?",
        "Task requirements?",
        "Which programming language?",
        "Will I get a certificate?",
    ]
    
    for suggestion in suggestions:
        if st.button(
            f"💬 {suggestion}",
            key=f"suggestion_{suggestion}",
            use_container_width=True
        ):
            # Add suggestion as user input
            st.session_state[config.SESSION_MESSAGES].append({
                "role": "user",
                "content": suggestion,
                "match_result": None
            })
            
            # Get response
            response = chatbot.ask(suggestion)
            
            st.session_state[config.SESSION_MESSAGES].append({
                "role": "assistant",
                "content": response.message,
                "match_result": response.match_result
            })
            
            st.rerun()