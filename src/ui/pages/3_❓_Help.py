"""
Help Page
User guide and documentation
"""
import streamlit as st

from src.ui.components import apply_custom_styles


def main() -> None:
    """Help page main function."""
    st.set_page_config(
        page_title="Help - FAQ Chatbot",
        page_icon="❓",
        layout="wide"
    )
    
    apply_custom_styles()
    
    st.title("❓ Help & Documentation")
    st.markdown("---")
    
    # Table of Contents
    st.markdown("""
        ## 📑 Table of Contents
        - [Getting Started](#getting-started)
        - [How to Use](#how-to-use)
        - [Features](#features)
        - [Tips for Best Results](#tips-for-best-results)
        - [FAQ](#faq)
        - [Contact Support](#contact-support)
    """)
    
    st.markdown("---")
    
    # Getting Started
    st.markdown("## 🚀 Getting Started")
    st.markdown("""
        Welcome to the CodeAlpha FAQ Chatbot! This intelligent assistant helps you find answers to 
        questions about CodeAlpha internships using Natural Language Processing.
        
        **What you can do:**
        - Ask questions in natural language
        - Browse FAQs by category
        - Search by keywords
        - Get instant answers with confidence scores
    """)
    
    st.markdown("---")
    
    # How to Use
    st.markdown("## 💡 How to Use")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            ### Asking Questions
            1. Type your question in the chat input at the bottom
            2. Press Enter or click Send
            3. The chatbot will find the most relevant answer
            4. View the confidence score to see match quality
            
            **Example Questions:**
            - "What is CodeAlpha?"
            - "How do I apply for the internship?"
            - "What certificates will I receive?"
        """)
    
    with col2:
        st.markdown("""
            ### Browsing FAQs
            1. Use the sidebar to browse by category
            2. Click on any question to see the answer
            3. Use the search box to find specific topics
            4. Try the quick suggestions for common questions
            
            **Categories Available:**
            - General
            - Technical
            - Account
            - Billing
            - Product
        """)
    
    st.markdown("---")
    
    # Features
    st.markdown("## ✨ Features")
    
    features = [
        {
            "icon": "🤖",
            "title": "Intelligent Matching",
            "description": "Uses TF-IDF and cosine similarity to find the best matching answers"
        },
        {
            "icon": "📊",
            "title": "Confidence Scores",
            "description": "Shows how confident the chatbot is about each answer"
        },
        {
            "icon": "💬",
            "title": "Natural Language",
            "description": "Ask questions in your own words - no special syntax needed"
        },
        {
            "icon": "📁",
            "title": "Category Browsing",
            "description": "Browse FAQs organized by topic and category"
        },
        {
            "icon": "🔍",
            "title": "Keyword Search",
            "description": "Find FAQs quickly using keyword search"
        },
        {
            "icon": "💡",
            "title": "Smart Suggestions",
            "description": "Get alternative suggestions for low-confidence matches"
        },
        {
            "icon": "📜",
            "title": "Conversation History",
            "description": "Keep track of your questions and answers"
        },
        {
            "icon": "📊",
            "title": "Statistics Dashboard",
            "description": "View analytics and insights about the chatbot"
        }
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
                ### {feature['icon']} {feature['title']}
                {feature['description']}
            """)
    
    st.markdown("---")
    
    # Tips for Best Results
    st.markdown("## 💎 Tips for Best Results")
    
    st.info("""
        **✅ DO:**
        - Ask clear, specific questions
        - Use complete sentences
        - Try different phrasings if you don't get good results
        - Check the confidence score
        - Browse categories if you're not sure what to ask
        
        **❌ DON'T:**
        - Use very short queries (less than 3 words)
        - Include special characters or emojis
        - Ask questions outside the domain (CodeAlpha internships)
        - Expect answers to questions not in the FAQ database
    """)
    
    st.markdown("---")
    
    # FAQ
    st.markdown("## 🔎 Frequently Asked Questions")
    
    with st.expander("❓ How does the chatbot work?"):
        st.markdown("""
            The chatbot uses Natural Language Processing (NLP) to understand your questions:
            
            1. **Preprocessing**: Your question is cleaned and normalized
            2. **Vectorization**: Text is converted to numerical vectors using TF-IDF
            3. **Matching**: Cosine similarity finds the most similar FAQ
            4. **Response**: The answer is returned with a confidence score
        """)
    
    with st.expander("❓ What does the confidence score mean?"):
        st.markdown("""
            The confidence score shows how well your question matches an FAQ:
            
            - **High (70-100%)**: Excellent match, answer is very relevant
            - **Medium (50-69%)**: Good match, answer is probably relevant
            - **Low (30-49%)**: Weak match, answer might not be what you're looking for
            - **No Match (<30%)**: No good match found, try rephrasing
        """)
    
    with st.expander("❓ Why didn't I get an answer?"):
        st.markdown("""
            Possible reasons:
            
            1. **Question not in database**: The FAQ database only covers CodeAlpha internship topics
            2. **Unclear question**: Try rephrasing more clearly
            3. **Too generic**: Be more specific about what you want to know
            4. **Spelling errors**: Check your spelling and try again
            
            **Solution**: Try browsing categories or using keyword search instead.
        """)
    
    with st.expander("❓ Can I suggest new FAQs?"):
        st.markdown("""
            Yes! If you have questions that aren't answered, please contact:
            
            - 📧 Email: services@codealpha.tech
            - 💬 WhatsApp: +91 8052293611
            
            We continuously update our FAQ database based on user feedback.
        """)
    
    with st.expander("❓ Is my conversation private?"):
        st.markdown("""
            Your conversation is stored only in your browser session and is automatically 
            cleared when you close the browser. We don't store or transmit your conversations 
            to any server.
        """)
    
    st.markdown("---")
    
    # Contact Support
    st.markdown("## 📞 Contact Support")
    
    st.success("""
        **Need more help?**
        
        Reach out to CodeAlpha support:
        
        - 🌐 **Website**: www.codealpha.tech
        - 📧 **Email**: services@codealpha.tech
        - 💬 **WhatsApp**: +91 8052293611
        
        Our team is here to help you with any questions or issues!
    """)
    
    st.markdown("---")
    
    # About
    st.markdown("## ℹ️ About This Chatbot")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            **Technology Stack:**
            - Python 3.11+
            - Streamlit (UI)
            - NLTK (NLP)
            - scikit-learn (ML)
            - TF-IDF Vectorization
            - Cosine Similarity
        """)
    
    with col2:
        st.markdown("""
            **Project Info:**
            - Version: 1.0.0
            - Task: CodeAlpha AI Internship Task 2
            - Type: FAQ Chatbot
            - License: MIT
        """)


if __name__ == "__main__":
    main()