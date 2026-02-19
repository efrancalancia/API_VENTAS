import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

# Thick mode requerido para Oracle 11g
oracledb.init_oracle_client(lib_dir=os.getenv("ORACLE_CLIENT_DIR"))

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "dsn": os.getenv("DB_DSN"),
}


def get_connection():
    return oracledb.connect(**DB_CONFIG)
