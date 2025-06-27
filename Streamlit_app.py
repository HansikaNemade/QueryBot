


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



# ---------- Prompt Generator ----------
def generate_prompt():
    pre_prompt = """  You are an expert in converting English questions to SQL queries!

        The SQL database has a tables  """

    # Create engine and inspector
    engine = create_engine(uri)
    inspector = inspect(engine)

    # Get all table names from public schema
    tables = inspector.get_table_names(schema='public')

    # Build schema string
    schema_str = ""

    for table in tables:
        schema_str += f"Table: {table}\n"

        # Columns
        columns = inspector.get_columns(table, schema='public')
        for col in columns:
            schema_str += f"  - {col['name']} ({col['type']})\n"

        # Primary Keys
        pk_cols = inspector.get_pk_constraint(table, schema='public').get('constrained_columns', [])
        if pk_cols:
            schema_str += f"  * Primary Key: {', '.join(pk_cols)}\n"

        # Foreign Keys
        fks = inspector.get_foreign_keys(table, schema='public')
        for fk in fks:
            local_cols = ', '.join(fk['constrained_columns'])
            ref_table = fk['referred_table']
            ref_cols = ', '.join(fk['referred_columns'])
            schema_str += f"  * Foreign Key: {local_cols} → {ref_table}({ref_cols})\n"

        schema_str += "\n"

    post_prompt = """  For example:
        - input :- How many employees are in the database?
          output:- SELECT COUNT(*) FROM emp;

        - input:- List all employees in the IT department.
          output:- SELECT * FROM emp WHERE DEPARTMENT = 'IT';

        Your tasks:
        1. Do NOT use backticks.
        2. Use valid PostgreSQL syntax.
        3. Only return the final SQL query.
        4. For INSERT, assume auto-generated empid, and optional deptid.
        """

    return pre_prompt + schema_str + post_prompt


# ---------- Query Executor ----------
def execute_query(query):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            json_result = [dict(zip(columns, row)) for row in result] if result else []
        else:
            connection.commit()
            json_result = "Query executed successfully!"
            cursor.close()
            connection.close()
            return json_result
    except Exception as e:
        return {"error": str(e)}





# ---------- Query Executor ----------
def execute_postgres_query(query: str):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute(query)

        if query.strip().upper().startswith("SELECT"):
            records = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(records, columns=columns)
            return df
        else:
            connection.commit()
            return "Query executed successfully."

    except Exception as e:
        return f"Error executing query: {e}"

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




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

    question = st.text_area("Enter your natural language query:")

    if st.button("Generate & Execute Query"):
        with st.spinner("Generating SQL Query..."):

            prompt = generate_prompt()
            full_input = f"{prompt}\n\nQuestion: {question}"
            generate_query = create_sql_query_chain(llm, db)
            sql_query = generate_query.invoke({"question": full_input}).replace("SQLQuery:", "").strip()
            st.code(sql_query, language="sql")

            query_results = execute_postgres_query(sql_query)

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




