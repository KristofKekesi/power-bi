"""
Logics regarding scraping data from ticketswap.com.
"""

from random import choice
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from modules.custom_logger import CustomLogger
from modules.data_classes import Event

class TicketSwapConnector:
	"""
	Connector class to get data from scraping 
	"""
	def __init__(self, headless=True):
		"""
		Init function make TicketSwapConnector class.
		"""
		self.logger = CustomLogger("TicketswapConnector")
		self.headless = headless
	
	def __call__(self, url: str):
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
			case "event": 
				self.logger.info("Using event scraping method.")
				return self.scrape_event(url._replace(fragment="").geturl())
			case "location": 
				self.logger.info("Using venue scraping method.")
				return self.scrape_venue(url._replace(fragment="").geturl())
			case "city": 
				self.logger.info("Using city scraping method.")
				return self.scrape_city(url._replace(fragment="").geturl())
	
	def __scrape(self, callback):
		"""
		Function to load url and returns page from it.
		"""
		with sync_playwright() as p:
			browser = p.chromium.launch(
				headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
			)

			devices = [
				"iPhone 11", "iPhone 11 Pro", "iPhone 11 Pro Max",
				"iPhone 12", "iPhone 12 Pro", "iPhone 12 Pro Max",
				"iPhone 13", "iPhone 13 Pro", "iPhone 13 Pro Max",
				"iPhone 14", "iPhone 14 Pro", "iPhone 14 Pro Max",
				"iPhone 15", "iPhone 15 Max", "iPhone 15 Pro", "iPhone 15 Pro Max",
			]
			device = p.devices[choice(devices)]
			context = browser.new_context(
				**device,
                locale="en-US",
                timezone_id="Europe/Budapest",
                extra_http_headers={
                  "accept-language": "en-US,en;q=0.9"
                }
			)

			# Hide webdriver flag
			context.add_init_script("""
                // hide webdriver
                Object.defineProperty(navigator, 'webdriver', {get:() => false});
                // mock Chrome object
                window.chrome = { runtime: {} };
                // fake plugins
                Object.defineProperty(navigator, 'plugins', {
                  get: () => [1,2,3,4,5]
                });
                // fake languages
                Object.defineProperty(navigator, 'languages', {
                  get: () => ['en-US','en']
                });
            """)

			page = context.new_page()
			output = callback(page)
			browser.close()

			return output
	
	def __scrape_site(self, url: str, timeout: int):
		"""
		General scraping functionality.
		Since the site's pages are generally the same
		we can use this function on every page.
		"""
		def callback(page):
			self.logger.info(f"Started scraping {url}. Timeout is set to {timeout/1_000}s.")
			page.goto(url, timeout=timeout, wait_until="domcontentloaded")

			# Wait for the events to show
			EVENTS_WRAPPER = "div:has(h2:has-text('Events'))"
			page.wait_for_selector(EVENTS_WRAPPER, timeout=timeout)

			# Close cookie banner
			COOKIE_BANNER = "button:has-text('Reject')"
			page.locator(COOKIE_BANNER).click()

			# Press 'Show more' while it is visible
			SHOW_MORE = "button:has-text('Show more')"
			buttons = page.locator(SHOW_MORE)
			while buttons.count() == 2:
				self.logger.debug("Pressing 'Show more' button.")
				try:
					more = buttons.first
					more.wait_for(state="visible", timeout=3_000)
					more.scroll_into_view_if_needed()
					more.click(timeout=5_000)
					page.wait_for_timeout(1_000)
				except Exception as error:
					self.logger.error(f"Could not click 'Show more' button. Error: {error}.")
					break

				# Re-query DOM
				buttons = page.locator(SHOW_MORE)
			
			# Check if got suspended
			page.wait_for_timeout(1_000)
			error_locator = page.locator("text=/Something went wrong.*Please contact us if this keeps happening/i")
			if error_locator.count():
				self.logger.warning(f"Anti-bot enabled. Could not scrape {url}")
				return []
			
			# Scrape events
			CARD = "a[href*='/event/']"
			elements = page.query_selector_all(CARD)
			self.logger.info(f"Identified {len(elements)} events to be scraped.")

			events = []
			for _, element in enumerate(elements, start=1):
				ticketswap_url = element.get_attribute("href")
				name = element.query_selector("h4").inner_text().strip()
				venue = element.query_selector("h5").inner_text().strip()
				date = element.query_selector(
					"div:has(svg[aria-label='CalendarAlt']) span"
				).inner_text().strip()

				events.append({
					"title":			name,
					"venue":			venue,
					"date":				date,
					"ticketswap_url":	ticketswap_url,
				})

			self.logger.info(f"Scraped {len(events)} events.")
			return events
		
		return self.__scrape(callback)

	def scrape_event(self, url: str, timeout=60_000):
		"""
		Function to scrape data from the event page.
		"""
		return self.__scrape_site(url, timeout)
			
	def scrape_venue(self, url: str, timeout=60_000):
		"""
		Function to scrape data from the venue page.
		"""
		return self.__scrape_site(url, timeout)
	
	def scrape_city(self, url: str, timeout=60_000):
		"""
		Function to scrape data from the city page.
		"""
		return self.__scrape_site(url, timeout)
		

if __name__ == "__main__":
	# Example usage
	logger = CustomLogger("Example")
	connector = TicketSwapConnector(headless=False)
	data = connector("https://www.ticketswap.com/location/akvarium-klub/13262")
	logger.info(data)