# QueryBot

# 🧠 AI-Powered SQL Query Generator & Executor

This is a **Streamlit-based web application** that uses **Google Gemini (via LangChain)** to convert natural language queries into SQL statements and execute them on a **PostgreSQL database**. It includes secure login, schema-based SQL generation, and query results display.

---

## 🚀 Features

- 🔐 User authentication with hashed passwords.
- 🧠 Converts natural language questions to SQL using Gemini 1.5 Flash.
- 🗂 Dynamically extracts table schema (columns, primary and foreign keys).
- 📊 Executes `SELECT`, `INSERT`, and other queries and shows results.
- 🌐 Built with Streamlit for a clean and simple UI.

---
## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/HansikaNemade/QueryBot.git
cd QueryBot
```

### 2.Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Configuration
Update the following in app.py:

```python
db_params = {
    "host": "localhost",
    "port": 5432,               # default PostgreSQL port no
    "database": "your_database_name",  # database name
    "user": "postgres",    # username
    "password": "your_actual_password" # password
}

GOOGLE_API_KEY = "your_gemini_api_key"
```
### 5. Run the Streamlit App
```bash
streamlit run Streamlit_app.py

```

