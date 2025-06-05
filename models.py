import pg8000
import os
from dotenv import load_dotenv

load_dotenv()

conn = pg8000.connect(
    user="postgres",
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_URL"),   # or your server address
    port=5432,          # default PostgreSQL port
    database="postgres"
)
cursor = conn.cursor()
