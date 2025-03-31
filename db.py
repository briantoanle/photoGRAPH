import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize a connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,  # Min 1, Max 10 connections
        dsn=DATABASE_URL,
        connect_timeout=5
    )
    if connection_pool:
        print("✅ PostgreSQL Connection Pool created successfully")
except Exception as e:
    print(f"❌ Error creating connection pool: {e}")
    connection_pool = None

# Function to get a new connection from the pool
def get_db_connection():
    if connection_pool:
        try:
            return connection_pool.getconn()
        except Exception as e:
            print(f"❌ Error getting a connection from the pool: {e}")
    return None

# Function to return the connection back to the pool
def close_db_connection(conn):
    if connection_pool and conn:
        connection_pool.putconn(conn)
