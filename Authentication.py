

import psycopg2
import bcrypt

# PostgreSQL DB credentials
db_user = "postgres"
db_password = "24Hansika24@"  # use plain format here, not URL-encoded
db_host = "localhost"
db_name = "employeedb1"

# Connect to PostgreSQL
connection = psycopg2.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    dbname=db_name
)
cursor = connection.cursor()

# User details
username = "Hansika"
plain_password = "hansi"

# Hash the password before storing
hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Insert query
query = "INSERT INTO users (username, password) VALUES (%s, %s)"
cursor.execute(query, (username, hashed_password))
connection.commit()

# Cleanup
cursor.close()
connection.close()
print("✅ User created successfully in PostgreSQL!")
