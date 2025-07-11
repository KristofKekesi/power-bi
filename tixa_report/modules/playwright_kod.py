import asyncio
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from modules.custom_logger import CustomLogger

async def leszedő(timeout: int=6000, headless=True):
    logger = CustomLogger("TixaConnector")

    veg = list()
    url = "https://www.tixa.hu"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        
        logger.info(f"Started scraping {url}. Timeout is set to {timeout/100}s.")
        await page.goto(url, timeout=timeout)
        
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        name_el2= await page.locator('[data-bind="text: name, attr: { href: url }"]').all()
        name_elements = await page.locator('[data-bind="text: data.name, attr: { href: data.url }"]').all()
        
        for index in range(len(name_el2)):
                    link = await name_el2[index].get_attribute("href")
                    veg.append(link)

        for index in range(len(name_elements)):
                if index > 4:
                    link = await name_elements[index].get_attribute("href")
                    veg.append(link)
        await browser.close()
    return veg

def scrape(timeout: int=15000, headless=True):
    logger = CustomLogger("TixaConnector")

    eredmeny = []
    links = asyncio.run(leszedő())    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        for url in links:
            page.goto(url)

            try:
                page.wait_for_selector('[data-bind*="locationName"]', timeout=timeout)
                page.wait_for_selector('[data-bind*="title"]', timeout=timeout)
                page.wait_for_selector('[data-bind*="startDate"]', timeout=timeout)

                location_element = page.query_selector('[data-bind*="locationName"]')

                location_name = location_element.inner_text() 
                location_href = location_element.get_attribute("href")

                title_element = page.query_selector('[data-bind*="title"]')
                event_title = title_element.inner_text()

                date_element = page.query_selector('[data-bind*="startDate"]')
                event_date = date_element.inner_text() 

                eredmeny.append([location_name,location_href,event_title,url,event_date])
            except TimeoutError as error:
                logger.error(error)

        browser.close()
   
    return eredmeny