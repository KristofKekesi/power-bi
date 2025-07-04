import asyncio
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

async def leszedő(timeout: int=6000, headless=True):
    veg = list()
    links = ["https://www.tixa.hu","https://www.tixa.hu/durerkert","https://www.tixa.hu/budapest_park",
        "https://www.tixa.hu/fogashaz_budapest","https://www.tixa.hu/turbina-kulturalis-kozpont"]

    with open(f"csaklinkek.txt","w",encoding="utf-8") as f:
        for i in range(len(links)):
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=headless)
                page = await browser.new_page()
                
                await page.goto(links[i], timeout=timeout)
                
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                
                name_elements = await page.locator('[data-bind="text: data.name, attr: { href: data.url }"]').all()
                if i == 0:
                    for index in range(len(name_elements)):
                        if index > 3:
                            link = await name_elements[index].get_attribute("href")
                            veg.append(link)
                            f.writelines(f"{link}\n")
                else:
                    for index in range(len(name_elements)):
                            link = await name_elements[index].get_attribute("href")
                            veg.append(link)
                            f.writelines(f"{link}\n")
                await browser.close()
    return veg

def scrape(timeout: int=15000, headless=True) -> None:
    asyncio.run(leszedő())
    linkek = []
    with open("csaklinkek.txt","r",encoding="utf-8") as f:
        for sor in f:
            linkek.append(sor)
    helyek = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        for url in linkek:
            page.goto(url)

            try:
                page.wait_for_selector('[data-bind*="locationName"]', timeout=timeout)
                page.wait_for_selector('[data-bind*="title"]', timeout=timeout)
                page.wait_for_selector('[data-bind*="startDate"]', timeout=timeout)

                location_element = page.query_selector('[data-bind*="locationName"]')

                location_name = location_element.inner_text() if location_element else "Nincs helynév"
                location_href = location_element.get_attribute("href") if location_element else "Nincs link"

                title_element = page.query_selector('[data-bind*="title"]')
                event_title = title_element.inner_text() if title_element else "Nincs cím"

                date_element = page.query_selector('[data-bind*="startDate"]')
                event_date = date_element.inner_text() if date_element else "Nincs dátum"
                
                helyek.append(location_name)
                print("Scrape eredmények:")
                print(f"Hely neve: {location_name}")
                print(f"Hely linkje: {location_href}")
                print(f"Esemény neve: {event_title}")
                print(f"Esemény linkje: {url}")
                print(f"Esemény ideje: {event_date}")

            except TimeoutError:
                print("Timeout")

        browser.close()
    with open("helyek.txt","w",encoding="utf-8")as f:
        for h in helyek:
            f.writelines(f'{h}\n')
