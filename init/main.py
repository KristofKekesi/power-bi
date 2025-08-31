import csv
import logging
from sys import stdout
from os import getenv, fsencode, listdir, path
from modules.db import connect_to_db, sanitize_row
from modules.custom_logger import CustomLogger

def main(logger: CustomLogger):
	def _upload_csv(connection, content, tablename):
		if isinstance(content, (bytes, bytearray)):
			content = content.decode("utf-8")

		# Split into lines for csv.DictReader
		lines = content.splitlines()
		reader = csv.DictReader(lines)
		cols = reader.fieldnames
		if not cols:
			raise ValueError("CSV content has no header row")

		# Build INSERT statement
		col_sql = ", ".join(f'"{c}"' for c in cols)
		placeholders = ", ".join(["%s"] * len(cols))
		insert_sql = (
			f'INSERT INTO "{tablename}" ({col_sql}) '
			f"VALUES ({placeholders})"
		)

		# Prepare data rows
		data = []
		for row in reader:
			clean = sanitize_row(row)
			data.append(tuple(clean[c] for c in cols))

		# Execute batch insert
		cur = connection.cursor()
		try:
			cur.executemany(insert_sql, data)
			connection.commit()
		except Exception as error:
			connection.rollback()
			logger.error(error)
			raise error
		finally:
			cur.close()

		logger.info(f"Inserted {len(data)} rows into {tablename}")

	def _import_batches(connection, directory="data"):
		batch_names = [
			name
			for name in listdir(directory)
			if name.isdigit() and path.isdir(path.join(directory, name))
		]

		batch_nums = sorted(int(n) for n in batch_names)
		for batch_num in batch_nums:
			batch_dir = str(batch_num)
			logger.info(f"Importing batch {batch_num}…")

			full_batch_path = path.join(directory, batch_dir)
			for fn in sorted(listdir(full_batch_path)):
				if not fn.endswith(".csv"):
					continue

				csv_path = path.join(full_batch_path, fn)
				with open(csv_path, encoding="utf-8") as f:
					content = f.read()

				tablename = path.splitext(fn)[0]
				_upload_csv(connection, content, tablename)

			logger.info(f"Finished importing batch {batch_num}.")
	
	# Purge all data if needed
	purge = getenv("PURGE_DB", "false");
	if (purge == "true"):
		logger.info("Deleting existing data...")

	# Connect to db
	user = getenv("POSTGRES_USER", "user")
	password = getenv("POSTGRES_PASSWORD", "password")
	database = getenv("POSTGRES_DB", "mock")
	host = getenv("POSTGRES_HOST", "postgres")
	port = getenv("POSTGRES_PORT", "5432")

	try:
		conn = connect_to_db(database, user, password, host, port)
		cursor = conn.cursor()
		logger.info("Connected to the database.")

		# Run init.sql
		with open("initialize.sql", "r") as file:
			sql = file.read()
			cursor.execute(sql)
		conn.commit()
		logger.info("Initiated schema.")

		# Import data in batches
		_import_batches(conn)
	except Exception as error:
		logger.error(error)
		raise error
	finally:
		cursor.close()

if __name__ == "__main__":
	logger = CustomLogger("db-init")
	
	logger.info("Starting...")
	main(logger)
	logger.info("Exiting successfully...")