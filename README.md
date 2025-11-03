# FAQ Chatbot - CodeAlpha AI Internship Task 2

An intelligent FAQ chatbot that uses Natural Language Processing to match user queries with relevant answers from a knowledge base.

## 🚀 Features
- Natural language question matching
- Cosine similarity-based answer retrieval
- Interactive Streamlit UI
- Confidence scoring
- Easy-to-update FAQ database

## 🛠️ Tech Stack
- Python 3.11+
- Streamlit (UI)
- NLTK (NLP)
- scikit-learn (ML)
- UV (Package Manager)

## 📦 Installation
```bash
# Clone repository
git clone <your-repo-url>
cd CodeAlpha_ChatbotFAQ

# Install dependencies using UV
uv pip install -e .
```

## 🏃 Running the Application
```bash
streamlit run src/main.py
```

## 🧪 Running Tests
```bash
pytest tests/ -v --cov=src
```

## 📁 Project Structure
```
CodeAlpha_ChatbotFAQ/
├── src/          # Source code
├── data/         # FAQ database
├── tests/        # Unit tests
└── assets/       # Static assets
```

## 👨‍💻 Author
[Your Name] - CodeAlpha AI Intern

## 📄 License
MIT License