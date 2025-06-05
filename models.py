import pg8000
import os
from dotenv import load_dotenv
# import ssl
#
#
# conn = None
'''
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

conn = pg8000.connect(
    user="postgres",
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_URL"),
    port=5432,
    database="postgres",
    ssl_context=ssl_context
)
'''
conn = pg8000.connect(
    user=os.getenv("DATABASE_USERNAME"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_URL"),
    port=5432,
    database=os.getenv("DATABASE_NAME")
)

cursor = conn.cursor()