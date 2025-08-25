"""
Logics regarding scraping data from bandsintown.com.
"""

from modules.custom_logger import CustomLogger
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from urllib.parse import urlparse
from modules.custom_logger import CustomLogger
from playwright.sync_api import sync_playwright

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

		self.logger.info(f"Identifying process to scrape URL ({url}) with...")
		parsed_url = urlparse(url)
		path = parsed_url.path.split("/")

		match path[1]:
			case "e": 
				self.logger.info("Using event scraping method.")
				return  self.scrape_event(parsed_url._replace(fragment="").geturl())
			case "v": 
				self.logger.info("Using event scraping method.")
				return  self.scrape_event(parsed_url._replace(fragment="").geturl())
			case "a": 
				self.logger.info("Using artist scraping method.")
				return  self.scrape_artist(parsed_url._replace(fragment="").geturl())
			
	def scrape_event(self, url: str):
		"""
		Function to scrape data from the event page.
		"""

		data = []
		with sync_playwright() as p:
			browser =  p.chromium.launch(headless=True)
			page =  browser.new_page()
			page.goto(url, wait_until='networkidle')
			
			place_name = page.query_selector('.i5s97858a8YcXS8Ht2a4')
			if place_name:
				place_name = page.locator('.i5s97858a8YcXS8Ht2a4').inner_text()
				events = [{
					"Place name":           place_name,
					"bandsintown_url":      url 
				}]

				# locating upcoming concerts
				links = page.locator('.tY_uoLiOK4FrxkcoAV7k').all()
				for link in links:
					link = link.get_attribute('href')
					event_url = link.split("?")[0]
					events.append(event_url)
				return events
			
			# locating event name			
			page.wait_for_selector('._FmG2rq5Aj0u3WF5Nunp')
			name =  page.locator('._FmG2rq5Aj0u3WF5Nunp').inner_text()

			# locating bandsintown_url of the place
			page.wait_for_selector('.cmjTos0Zxfv6k1J2SE4c')
			place_url =  page.locator('.cmjTos0Zxfv6k1J2SE4c').get_attribute('href')
			place_url = place_url.split("?")[0]

			data.append({
				"Event name":           name,
				"Place url":            place_url,
				"Bandsintown url":      url
			})
		return data

	def scrape_artist(self, url: str):
		"""
		Function to scrape data from the artist page.
		"""
		data = []
		with sync_playwright() as p:
			browser = p.chromium.launch(headless=True)
			page = browser.new_page()
			page.goto(url, wait_until='networkidle')
		
			# locating artist name
			page.wait_for_selector('h1')
			artist_name = page.locator('h1').inner_text()
			data.append({
				"Artist name":      artist_name,
				"Artist link":      url,
			})

			links = page.locator('a').all()
			link_list = []
			link_del = set()
			
			for link in links:
				url = link.get_attribute('href')
				href = link.get_attribute('href')
				if href:
					href = urlparse(href)
					path = href.path.split("/")
					if len(path) > 1:
						if path[1] == 'e':
							link_del.add(path[2])
							if len(link_list) != len(link_del):
								link_list.append(url)
								data.append(url.split('?')[0])
		return data

if __name__ == "__main__":
	logger = CustomLogger("Example")
	connector = BandsintownConnector()
	url = 'https://www.bandsintown.com/a/3959010'
	    # 'https://www.bandsintown.com/e/106959093-blahalouisiana-at-budapest-park'
	    # 'https://www.bandsintown.com/v/10121097-budapest-park'
	data =  connector(url)
	logger.info(data)

