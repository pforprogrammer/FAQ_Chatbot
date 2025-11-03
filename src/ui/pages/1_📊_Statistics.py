"""
Statistics Page
Detailed statistics and analytics dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.services.chatbot import Chatbot
from src.config import config
from src.ui.components import apply_custom_styles


def main() -> None:
    """Statistics page main function."""
    st.set_page_config(
        page_title="Statistics - FAQ Chatbot",
        page_icon="📊",
        layout="wide"
    )
    
    apply_custom_styles()
    
    st.title("📊 Chatbot Statistics & Analytics")
    st.markdown("---")
    
    # Get chatbot from session state
    if config.SESSION_CHATBOT not in st.session_state:
        st.error("❌ Chatbot not initialized. Please return to the main page.")
        return
    
    chatbot: Chatbot = st.session_state[config.SESSION_CHATBOT]
    stats = chatbot.get_statistics()
    
    # Overview metrics
    render_overview_metrics(stats)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        render_category_distribution(chatbot)
    
    with col2:
        render_conversation_stats(chatbot)
    
    st.markdown("---")
    
    # FAQ Details
    render_faq_details(chatbot)


def render_overview_metrics(stats: dict) -> None:
    """Render overview metrics cards."""
    st.markdown("### 📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total FAQs",
            value=stats['total_faqs'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Categories",
            value=stats['total_categories'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Conversation Turns",
            value=stats['conversation_turns'],
            delta=None
        )
    
    with col4:
        vocab_size = stats['matcher_stats']['vocabulary_size']
        st.metric(
            label="Vocabulary Size",
            value=vocab_size,
            delta=None
        )


def render_category_distribution(chatbot: Chatbot) -> None:
    """Render category distribution chart."""
    st.markdown("### 📁 FAQs by Category")
    
    categories = chatbot.get_all_categories()
    
    category_data = []
    for category in categories:
        faqs = chatbot.get_faqs_by_category(category)
        category_data.append({
            'Category': category.value.capitalize(),
            'Count': len(faqs)
        })
    
    df = pd.DataFrame(category_data)
    
    fig = px.bar(
        df,
        x='Category',
        y='Count',
        color='Category',
        title="FAQ Distribution by Category"
    )
    
    fig.update_layout(
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_conversation_stats(chatbot: Chatbot) -> None:
    """Render conversation statistics."""
    st.markdown("### 💬 Conversation Analysis")
    
    history = chatbot.get_conversation_history()
    
    if not history:
        st.info("No conversation history yet")
        return
    
    # Count messages by role
    user_msgs = sum(1 for msg in history if msg.role == "user")
    assistant_msgs = sum(1 for msg in history if msg.role == "assistant")
    
    # Count confidence levels
    high_conf = sum(
        1 for msg in history 
        if msg.match_result and msg.match_result.similarity_score >= 0.7
    )
    medium_conf = sum(
        1 for msg in history 
        if msg.match_result and 0.5 <= msg.match_result.similarity_score < 0.7
    )
    low_conf = sum(
        1 for msg in history 
        if msg.match_result and msg.match_result.similarity_score < 0.5
    )
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=['High Confidence', 'Medium Confidence', 'Low Confidence'],
        values=[high_conf, medium_conf, low_conf],
        hole=.3,
        marker_colors=['#4caf50', '#ff9800', '#f44336']
    )])
    
    fig.update_layout(
        title="Response Confidence Distribution",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_faq_details(chatbot: Chatbot) -> None:
    """Render detailed FAQ table."""
    st.markdown("### 📋 All FAQs")
    
    # Prepare data
    faq_data = []
    for faq in chatbot.faq_database.faqs:
        faq_data.append({
            'ID': faq.id,
            'Question': faq.question,
            'Category': faq.category.value.capitalize(),
            'Keywords': ', '.join(faq.keywords[:3]),
            'Alternates': len(faq.alternate_questions)
        })
    
    df = pd.DataFrame(faq_data)
    
    # Display with filters
    selected_category = st.selectbox(
        "Filter by category",
        options=["All"] + [cat.value.capitalize() for cat in chatbot.get_all_categories()]
    )
    
    if selected_category != "All":
        df = df[df['Category'] == selected_category]
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    st.info(f"Showing {len(df)} of {len(faq_data)} FAQs")


if __name__ == "__main__":
    main()