from urllib.parse import urlparse
from playwright.async_api import async_playwright
import asyncio
import re
from modules.custom_logger import CustomLogger

class TixaConnector:
    def __init__(self, headless=True):
        self.logger = CustomLogger("TixaConnector")
        self.headless = headless

    async def __call__(self, url: str):
        """
        Run scrape logic based on the URL provided.
        """
        self.logger.info(f"Identifying process to scrape URL ({url}) with...")

        parsed_url = urlparse(url)
        path = parsed_url.path.split("/")

        if len(path) == 1 or path[1] == "":
            self.logger.info("Using mainpage scraping method.")
            return await self.mainpage(parsed_url._replace(fragment="").geturl())
        else:
            self.logger.info("Using event scraping method.")
            return await self.scrape_event(parsed_url._replace(fragment="").geturl())

    async def _scroll(self, page, max_iteration=25, wait=2):
        """
        Function to scroll down to the bottom of the page.
        """
        previous_height = None
        for _ in range(max_iteration):
            current_height = await page.evaluate("document.body.scrollHeight")
            if previous_height == current_height:
                break
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            previous_height = current_height
            await asyncio.sleep(wait)

    async def _scrape_event(self, url: str, timeout: int):
        events = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout)

            #Scraping for if it is just an event
            location_name2 = await page.query_selector('[data-bind*="locationName"]')
            event_title2 = await page.query_selector('[data-bind*="title"]')
            event_date2 = await page.query_selector('[data-bind*="startDate"]')
            if location_name2 and event_title2 and event_date2:
                location_name = await location_name2.inner_text()
                location_href = await location_name2.get_attribute('href')
                event_title = await event_title2.inner_text()
                event_date = await event_date2.inner_text()
                events.append({
                    "title": event_title,
                    "venue": location_name,
                    "venue_url": location_href,
                    "date": event_date,
                    "tixa_url": url,
                })
                return events

            #Scraping for if it is a place with events
            event_title = '[data-bind*="text: data.name"]'
            location_name = '[data-bind="text: data.location.name"]'
            event_date = '[data-bind="text: data.customDate || data.startDate"]'
            #locating all of the events
            await page.wait_for_selector(event_title, timeout=5000)
            await page.wait_for_selector(location_name, timeout=5000)
            await page.wait_for_selector(event_date, timeout=5000)
            #saving all the events
            event_titles = await page.query_selector_all(event_title)
            location_name = await page.query_selector_all(location_name)
            event_dates = await page.query_selector_all(event_date)

            for i in range(len(event_titles)):
                events.append({
                    "title": await event_titles[i].inner_text(),
                    "venue": await location_name[i].inner_text(),
                    "venue_url": url,
                    "date": await event_dates[i].inner_text(),
                    "tixa_url": await event_titles[i].get_attribute('href'),
                })

            await browser.close()
        return events

    async def _scrape_mainpage(self, url: str, timeout: int):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            self.logger.info(f"Started scraping {url}. Timeout is set to {timeout/1000}s.")
            await page.goto(url, timeout=timeout)
            await self._scroll(page)

            name_elements = await page.locator('[data-bind="text: data.name, attr: { href: data.url }"]').all()

            for elem in name_elements:
                link = await elem.get_attribute("href")
                if link:
                    await self.__call__(link)

            await browser.close()

    async def mainpage(self, url: str, timeout=60_000):
        """
        Function to scrape data from the mainpage.
        """
        return await self._scrape_mainpage(url, timeout)

    async def scrape_event(self, url: str, timeout=60_000):
        """
        Function to scrape data for an exact event.
        """
        return await self._scrape_event(url, timeout)


if __name__ == "__main__":
    async def main():
        logger = CustomLogger("Example")
        connector = TixaConnector(headless=False)
        url = "https://www.tixa.hu/jolvanezigy-evadzaro-20250724"
        #url = "https://www.tixa.hu/durerkert" 
        data = await connector(url)
        logger.info(data)

    asyncio.run(main())
