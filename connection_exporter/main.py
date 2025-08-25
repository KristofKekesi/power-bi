from modules.custom_logger import CustomLogger
from croniter import croniter
from datetime import datetime
from os import getenv
import asyncio
import traceback

def connectionImporter() -> None:
	# Get connections
	sql = '''
	SELECT artist_id, event_id, subevent_id, place_id, tixa_url, ticket_url, bandsintown_url
	FROM urls
	WHERE tixa_url IS NOT NULL or ticket_url IS NOT NULL or bandsintown_url IS NOT NULL;
	'''

	# Delete all data from the connections table.
	raise NotImplementedError

	# Load connections into the db.
	raise NotImplementedError

async def scheduler(function, cron_expression: str = "0 */6 * * *"):
	"""
	Run function based on cron schedule.
	"""

	logger = CustomLogger("Scheduler")

	try:
		cron = croniter(cron_expression, datetime.now())
		logger.info(f"Starting scheduler with cron expression: '{cron_expression}'.")
	except Exception as e:
		logger.error(f"Invalid cron expression '{cron_expression}': {str(e)}")
		return
	
	while True:
		try:
			# Calculate next execution time
			next_run = cron.get_next(datetime)
			wait_seconds = (next_run - datetime.now()).total_seconds()
			
			logger.info(f"Next execution scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')} "
					f"(in {wait_seconds:.0f} seconds)")
			
			# Wait until next scheduled time
			if wait_seconds > 0:
				await asyncio.sleep(wait_seconds)
			
			# Execute the importer
			start_time = datetime.now()
			logger.info("Starting function execution...")
			
			function()
			
			execution_time = (datetime.now() - start_time).total_seconds()
			logger.info(f"Function completed in {execution_time:.2f} seconds.")
			
		except Exception as e:
			logger.error(f"Error running function: {str(e)}")
			logger.error(f"Traceback: {traceback.format_exc()}")
			
			# On error, wait a bit before trying to calculate next run time
			await asyncio.sleep(60)
			

if __name__ == "__main__":
	logger = CustomLogger("ConnectionImporter")
	logger.info("Starting...")

	cron_expression = getenv("CONNECTION_IMPORTER_SCHEDULE", "0 */6 * * *")

	scheduler(connectionImporter, cron_expression=cron_expression)

	logger.info("Exiting...")