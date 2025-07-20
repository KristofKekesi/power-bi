from modules.custom_logger import CustomLogger
from time import sleep
from random import choice
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from modules.custom_logger import CustomLogger
import re

# Here goes the refactored version of 'playwright_kod.py'.


def has_number(s):
    """
    Returns True if the string contains any digit, False otherwise.
    """
    return bool(re.search(r'\d', s))

#This function scrolling to the end of the documents
def scroll(page):
	previous_height = None
	max_scrolls = 10  # safety limit

	for _ in range(max_scrolls):
		current_height = page.evaluate("document.body.scrollHeight")
		if previous_height == current_height:
			break  # no more scrolling possible
		page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
		previous_height = current_height
		sleep(2)


class TixaConnector:
	def __init__(self,headless=True):
		self.logger = CustomLogger("TixaConnector")
		self.headless = headless

	def __call__(self):
		"""
		Run scrape logic for a URL on call.
		"""
		"""
		Function to handle url based scraping.
		"""
		self.logger.info(f"Identifying process to scrape URL ({url}) with...")
		url = urlparse(url)
		path = url.path.split("/")
		match path[1]:
			case "":						#mainpage url
					self.logger.info("Using mainpage scraping method.") 
					return self.mainpage(url._replace(fragment="").geturl())
			case _:
				if has_number(path[1]): 	#event url which contain numbers
					self.logger.info("Using event scraping method.")
					return self.scrape_event(url._replace(fragment="").geturl())
				else:						#place url what not contain numbers
					self.logger.info("Using place scraping method.")
					return self.scrape_place(url._replace(fragment="").geturl())

	def _scrape_event(self, url: str, timeout: int):
		logger = CustomLogger("TixaConnector")
		events = []
		with sync_playwright() as p:
			browser = p.chromium.launch(headless=True)
			page = browser.new_page()
			page.goto(url)

			location_name = page.query_selector('[data-bind*="locationName"]').inner_text() 
			location_href = page.query_selector('[data-bind*="locationName"]').get_attribute("href")
			event_title = page.query_selector('[data-bind*="title"]').inner_text()
			event_date = page.query_selector('[data-bind*="startDate"]').inner_text()
			
			events.append({
					"title":			event_title,
					"venue":			location_name,
					"venue_url":		location_href,
					"date":				event_date,
					"tixa_url":			url,
				})
			
			browser.close()
		return events

	def _scrap_page(self, url: str, timeout: int):
		with sync_playwright() as p:
			browser = p.chromium.launch(headless=True)
			page = browser.new_page()
			
			self.logger.info(f"Started scraping {url}. Timeout is set to {timeout/100}s.")
			page.goto(url, timeout=timeout)
			#Scroll donw to be able to locate all elements in the webpage
			scroll(page)

			#Getting all the url on the main page and calling url sorting function
			name_elements = page.locator('[data-bind="text: data.name, attr: { href: data.url }"]').all()
			for index in range(len(name_elements)):
						link = name_elements[index].get_attribute("href")
						__call__(link)
			browser.close()

	#Same as scraping venu
	def mainpage(self, url: str, timeout=60_000):
		"""
		Function to scrape data from the main page.
		"""
		_scrap_page(url, timeout) 
	def scrape_place(self, url: str, timeout=60_000):
		"""
		Function to scrape data from the place page.
		"""
		_scrap_page(url,timeout)
	def scrape_event(self, url: str, timeout=60_000):
		"""
		Function to scrape data for an exact event.
		"""
		_scrape_event(url, timeout)


if __name__ == "__main__":
	# Example usage
	logger = CustomLogger("Example")
	connector = TixaConnector(headless=False)
	data = connector("https://www.tixa.hu/durerkert")
	logger.info(data)