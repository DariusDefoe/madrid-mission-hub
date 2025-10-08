import os, mysql.connector
from dotenv import load_dotenv
load_dotenv()

def get_cnx():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", "ChangeMeUser!"),
        database=os.getenv("DB_NAME", "vat_refunder"),
        autocommit=True,
    )
