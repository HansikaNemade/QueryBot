

import streamlit as st
import base64
import psycopg2

import bcrypt
import google.generativeai as genai
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine, inspect




# ---------- Database Configuration ----------
db_params = {
    "host": "localhost",
    "port": 5432,               # default PostgreSQL port no
    "database": "employeedb1",  # database name
    "user": "postgres",    # username
    "password": "24Hansika24@" # password
}

db_password= "24Hansika24%40"  # password to create uri



# SQLAlchemy URI for LangChain SQLDatabase
uri = f"postgresql+psycopg2://{db_params['user']}:{db_password}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
db = SQLDatabase.from_uri(uri)


# ---------- Initialize Google Gemini LLM ----------
GOOGLE_API_KEY = "AIzaSyAuTokV60KGykhTBSUvSgZhA6WjI4HO_mY"
genai.configure(api_key=GOOGLE_API_KEY)
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", google_api_key=GOOGLE_API_KEY)


# ---------------- Agent Classes ----------------


#     Schema Extractor Agent
class SchemaExtractorAgent:
    def __init__(self, uri):
        self.engine = create_engine(uri)
        self.inspector = inspect(self.engine)

    def extract_schema(self):
        schema_str = ""

        tables = self.inspector.get_table_names(schema='public')

        for table in tables:
            schema_str += f"Table: {table}\n"

            columns = self.inspector.get_columns(table)

            for col in columns:
                schema_str += f"  - {col['name']} ({col['type']})\n"

            # primary key inference
            pk = self.inspector.get_pk_constraint(table).get('constrained_columns', [])
            if pk:
                schema_str += f"  * Primary Key: {', '.join(pk)}\n"

            # foreign key inference
            fks = self.inspector.get_foreign_keys(table)
            for fk in fks:
                local_cols = ', '.join(fk['constrained_columns'])
                ref_table = fk['referred_table']
                ref_cols = ', '.join(fk['referred_columns'])
                schema_str += f"  * Foreign Key: {local_cols} → {ref_table}({ref_cols})\n"
            schema_str += "\n"
        return schema_str



#   Query Generator Agent
class SQLGeneratorAgent:
    def __init__(self, llm, db):
        self.chain = create_sql_query_chain(llm, db)

    def generate_sql(self, question, schema):
        prompt = f"""You are an expert in converting English to SQL queries.

{schema}

- input :- How many employees are in the database?
  output:- SELECT COUNT(*) FROM emp;
- input:- List all employees in the IT department.
  output:- SELECT * FROM emp WHERE department = 'IT';

Only output the SQL query. Do not use backticks.

Question: {question}
"""
        return self.chain.invoke({"question": prompt}).replace("SQLQuery:", "").strip()




#   Query Executor Agent
class PostgresExecutorAgent:
    def __init__(self, db_params):
        self.db_params = db_params

    def run_query(self, query):
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=columns)
            else:
                conn.commit()
                return "Query executed successfully."
        except Exception as e:
            return f"Error: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()



# ---------- Utility: Background Image ----------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)


# ---------- User Authentication ----------
def verify_user(username, password):
    try:
        # connection = psycopg2.connect(
        #     host=db_host,
        #     user=db_user,
        #     password=db_password,
        #     dbname=db_name
        # )

        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            return bcrypt.checkpw(password.encode('utf-8'), user_data[0].encode('utf-8'))
        return False

    except Exception as e:
        st.error(f"Database Error: {e}")
        return False




# ---------- Streamlit App UI ----------
add_bg_from_local("img1.jpg")


# Streamlit App
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login to Access AI-Powered SQL Generator")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.authenticated = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Credentials. Try again.")
else:

    # Main App UI
    st.title("LLM-Powered SQL QueryBot")
    st.subheader("Convert Natural Language to SQL and Execute It on PostgreSQL Database")

    #query_type = st.radio("Select Query Type:", ("Retrieve Data", "Insert Data"))

    schema_agent = SchemaExtractorAgent(uri)
    sql_agent = SQLGeneratorAgent(llm, db)
    exec_agent = PostgresExecutorAgent(db_params)

    question = st.text_area("Enter your natural language question:")

    if st.button("Generate & Execute Query"):
        with st.spinner("Processing..."):

            schema = schema_agent.extract_schema()
            sql = sql_agent.generate_sql(question, schema)
            st.code(sql, language="sql")
            query_results = exec_agent.run_query(sql)

            if isinstance(query_results, pd.DataFrame):
                st.write("### 📊 Query Results")
                st.dataframe(query_results)
            else:
                st.info(query_results)

if st.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()



#Count number of employees per department
#count of salaries paid in each department
#Find the maximum and minimum salary
#Count number of employees per department
#Find all employees with their titles
#List all employees with their department names
#Count employees by gender
#List managers and the departments they manage
#Find highest paid employee with name
#Get all titles do not limit
#सभी कर्मचारियों की सूची उनके विभाग के नाम के साथ



