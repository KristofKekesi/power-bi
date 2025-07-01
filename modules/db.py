from psycopg2 import sql, connect

def connect_to_db(dnname: str, user: str, password: str, host: str, port: int):
	# Database connection configuration
	DB_CONFIG = {
		"dbname": dnname,
		"user": user,
		"password": password,
		"host": host,
		"port": port,
	}

	"""Establish a connection to the database."""
	try:
		conn = connect(**DB_CONFIG)
		return conn
	except Exception as e:
		print(f"Error connecting to the database: {e}")
		exit(1)
		
def sanitize_row(row):
	"""
	Replace empty strings in the row dictionary with None (NULL in SQL).
	"""
	return {key: (value if value != '' else None) for key, value in row.items()}