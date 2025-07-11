from psycopg2 import connect
from modules.custom_logger import CustomLogger

def connect_to_db(dbname: str, user: str, password: str, host: str, port: int):
	logger = CustomLogger("ConnectToDB")

	# Database connection configuration
	DB_CONFIG = {
		"dbname": dbname,
		"user": user,
		"password": password,
		"host": host,
		"port": port,
	}

	"""Establish a connection to the database."""
	try:
		conn = connect(**DB_CONFIG)
		logger.info(f"Successfully connected to the database.")
		return conn
	except Exception as e:
		logger.error(f"Error connecting to the database: {e}")
		exit(1)
		
def sanitize_row(row):
	"""
	Replace empty strings in the row dictionary with None (NULL in SQL).
	"""
	return {key: (value if value != '' else None) for key, value in row.items()}