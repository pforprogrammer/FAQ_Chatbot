"""
Main Streamlit Application
Entry point for the FAQ Chatbot web interface
"""
import streamlit as st
from pathlib import Path

from src.services.chatbot import Chatbot
from src.config import config
from src.ui.components import (
    render_header,
    render_chat_interface,
    render_sidebar,
    initialize_session_state,
    apply_custom_styles
)


def main() -> None:
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title=config.page_title,
        page_icon=config.page_icon,
        layout=config.layout,
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_interface()


if __name__ == "__main__":
    main()