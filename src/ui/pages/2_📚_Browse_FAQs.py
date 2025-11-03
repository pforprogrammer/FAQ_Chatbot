"""
FAQ Browser Page
Browse and search all available FAQs
"""
import streamlit as st

from src.services.chatbot import Chatbot
from src.config import config
from src.ui.components import apply_custom_styles


def main() -> None:
    """FAQ Browser page main function."""
    st.set_page_config(
        page_title="Browse FAQs - FAQ Chatbot",
        page_icon="📚",
        layout="wide"
    )
    
    apply_custom_styles()
    
    st.title("📚 Browse All FAQs")
    st.markdown("---")
    
    # Get chatbot from session state
    if config.SESSION_CHATBOT not in st.session_state:
        st.error("❌ Chatbot not initialized. Please return to the main page.")
        return
    
    chatbot: Chatbot = st.session_state[config.SESSION_CHATBOT]
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search FAQs",
            placeholder="Enter keywords or question...",
            key="faq_search"
        )
    
    with col2:
        selected_category = st.selectbox(
            "📁 Filter by Category",
            options=["All"] + [cat.value.capitalize() for cat in chatbot.get_all_categories()]
        )
    
    st.markdown("---")
    
    # Get FAQs based on filters
    if selected_category == "All":
        faqs = chatbot.faq_database.faqs
    else:
        from src.models.faq import FAQCategory
        cat = FAQCategory(selected_category.lower())
        faqs = chatbot.get_faqs_by_category(cat)
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        faqs = [
            faq for faq in faqs
            if search_lower in faq.question.lower() 
            or search_lower in faq.answer.lower()
            or any(search_lower in kw.lower() for kw in faq.keywords)
        ]
    
    # Display results
    st.markdown(f"### Found {len(faqs)} FAQ(s)")
    
    if not faqs:
        st.info("No FAQs match your search criteria")
        return
    
    # Display FAQs
    for faq in faqs:
        with st.expander(f"❓ {faq.question}"):
            st.markdown(f"**Answer:**")
            st.markdown(faq.answer)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Category:** `{faq.category.value.capitalize()}`")
                if faq.keywords:
                    st.markdown(f"**Keywords:** {', '.join(faq.keywords)}")
            
            with col2:
                if faq.alternate_questions:
                    st.markdown(f"**Alternate Questions:** {len(faq.alternate_questions)}")
                    for i, alt_q in enumerate(faq.alternate_questions, 1):
                        st.markdown(f"{i}. {alt_q}")
            
            # Ask this question button
            if st.button(f"💬 Ask this question", key=f"ask_{faq.id}"):
                # Navigate back to main page and ask question
                st.session_state["auto_ask"] = faq.question
                st.switch_page("src/main.py")


if __name__ == "__main__":
    main()