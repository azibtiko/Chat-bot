# SupportLens - Customer Support Chatbot Observability Platform

## Setup Instructions

1. Clone the repository
2. Set up environment variables (copy .env.example to .env and add your LLM API key)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `uvicorn main:app --reload --port 8000`
5. Open `frontend/index.html` in your browser

## Setup Database

1. Create Database 
2. Paste Database name in .env file
3. run this command `python3 migrate.py`