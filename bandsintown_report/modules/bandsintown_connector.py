"""
Logics regarding scraping data from bandsintown.com.
"""

from urllib.parse import urlparse
from modules.custom_logger import CustomLogger

# Returns:
# - place:
#	- name (str)
#	- bandsintown_url (str)
#	- events (list[str]): list of the bandsintown_url-s of events
# - event:
#	- name (str)
#	- place (str): bandsintown_url of the place
#	- bandsintown_url (str)
#	- artists (list[str]): list of the bandsintown_url-s of artists
# - artist:
#	- name (str)
#	- bandsintown_url (str)
#	- events (list[str]): list of the bandsintown_url-s of events

class BandsintownConnector:
	"""
	Connector class to get data from scraping 
	"""
	def __init__(self):
		self.logger = CustomLogger("BandsintownConnector")
	def __call__(self, url: str):
		"""
		Function to handle url based scraping.
		"""
		self.logger(f"Identifying process to scrape URL ({url}) with...")

		url = urlparse(url)
		path = url.path.split("/")
		match path[0]:
			case "/e": 
				self.logger("Using event scraping method.")
				return self.scrape_event(url)
			case "/v": 
				self.logger("Using venue scraping method.")
				return self.scrape_venue(url)
			case "/a": 
				self.logger("Using artist scraping method.")
				return self.scrape_artist(url)
	def scrape_event(self, url: str):
		"""
		Function to scrape data from the event page.
		"""
		# Note: scrape data from url like 'https://www.bandsintown.com/e/1035476172'
	def scrape_venue(self, url: str):
		"""
		Function to scrape data from the venue page.
		"""
		# Note: scrape data from url like 'https://www.bandsintown.com/v/10121097'
	def scrape_artist(self, url: str):
		"""
		Function to scrape data from the artist page.
		"""
		# Note: scrape data from url like 'https://www.bandsintown.com/a/3959010'

if __name__ == "__main__":
	# Example usage
	connector = BandsintownConnector()
	data = connector("https://www.bandsintown.com/a/3959010")
