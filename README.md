# 🤖 Jids - AI Assistant with Document Q&A

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge)

A sophisticated Django-based AI assistant that can read, understand, and answer questions from uploaded documents using Retrieval-Augmented Generation (RAG).

##  Features

- ** Intelligent Chat Interface** - Conversational AI assistant with context awareness
- ** Multi-format Document Support** - Upload and process PDF, TXT, DOCX files
- ** Semantic Document Search** - Find relevant information across all uploaded documents
- ** RAG-powered Answers** - Responses grounded in your document content
- ** Session Management** - Persistent chat history across sessions
- ** Responsive UI** - Clean, modern interface that works on all devices
- ** Secure File Handling** - Temporary file storage with automatic cleanup

##  Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Git

### Installation

1. **Clone the repository**
git clone https://github.com/sarraz13/jids-ai-assistant.git
cd jids-ai-assistant
Set up virtual environment

bash
# Create virtual environment
python -m venv venv

# Activate it
Windows:
venv\Scripts\activate
Mac/Linux:
source venv/bin/activate
Install dependencies


pip install -r requirements.txt
Configure environment variables


# Copy the example environment file
cp .env.example .env

# Edit .env with your OpenAI API key
Use any text editor to add: OPENAI_API_KEY=your_actual_key_here
# Set up the database

python manage.py migrate
Start the development server

python manage.py runserver
Open in your browser

http://localhost:8000
🎯 Usage Guide
First Time Setup
Open http://localhost:8000 in your browser

Enter your name when prompted

Start chatting with Jids!


# 🛠️ Technology Stack
Backend
Django 5.2 - Web framework

Django REST Framework - API construction

SQLite - Database (development)

AI & Machine Learning
LangChain - AI agent framework

OpenAI GPT-4/GPT-3.5 - Language model

FAISS - Vector similarity search

Sentence Transformers - Text embeddings

Document Processing
PyPDF2 / pdfplumber - PDF text extraction

python-docx - Word document parsing

Unstructured - File type detection

Frontend
HTML5 / CSS3 - Structure and styling

Vanilla JavaScript - Interactive features

Fetch API - Server communication
