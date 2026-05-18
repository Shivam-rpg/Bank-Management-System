import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def connect_to_database():

    try:

        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

        print("Connected to the database successfully!")

        return connection

    except Exception as e:

        print(f"Error connecting to the database: {e}")

        return None


if __name__ == "__main__":

    conn = connect_to_database()

    if conn:
        conn.close()
        print("Database connection closed.")