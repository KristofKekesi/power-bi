import re
from os import getenv
from psycopg2 import sql
from datetime import date
from unidecode import unidecode
from modules.db import connect_to_db
from modules.pdf import Title, Data, PDFData
from tixa_scraper.modules.tixa_connector import TixaConnector
from modules.custom_logger import CustomLogger

"""
Class to make riports about tixa.hu data.
"""
class TixaConnector:
    def __init__(self, DB_CONFIG):
        self.logger = CustomLogger("TixaConnector")
        self.DB_CONFIG = DB_CONFIG
    """
    Function to make a report about the data of tixa.hu.
    """
    def make_report(self, filename:str="output.pdf", show_success:bool=False):
        # Making conenction to the db.
        connection = connect_to_db(**DB_CONFIG)
        cursor = connection.cursor()

        self.logger.info("Scraping tixa.hu...")
        result = scrape()   # Example return: [
                            #                 ['place_name', 'place_tixa_url', 
                            #                  'event_name', 'event_tixa_url',
                            #                  'FULL MONTH DAY, YYYY HH:MM'
                            #                 ]

        # Removing special characrers (TODO: make special characters show up in the PDF.)
        for i, single in enumerate(result):
            for j, item in enumerate(single):
                result[i][j] = unidecode(item)

        """
        Utility function to clean titles.
        """
        def remove(text):
            # Remove all chars after '//'
            pattern = r'\s(@|//).*'
            return re.sub(pattern, '', text).rstrip()

        """
        Function to get distinct places from the scraped data.
        """
        def places() -> list[list]:
            seen = set()
            unique_pairs = []

            for single in result:
                place_name, place_tixa_url, _, _, _ = single
                t = (place_name, place_tixa_url)
                if t not in seen:
                    seen.add(t)
                    unique_pairs.append([place_name, place_tixa_url])
            return unique_pairs
        
        """
        Function to evaluate places.
        """
        def eval_places() -> list[Data]:
            scraped_places = places()

            serialized = []
            for place in scraped_places:
                place_name, place_tixa_url = place

                query = sql.SQL("""
                                SELECT place.id, place.name, url.tixa_url
                                FROM urls url
                                JOIN places place ON place.id = url.place_id
                                WHERE url.tixa_url = %s OR place.name LIKE %s;
                            """)

                cursor.execute(query, (place_tixa_url, place_name))
                rows = cursor.fetchall()

                status = "fail"
                description = "A helyszin nem talalhato az adatbazisban."
                link = place_tixa_url
                for row in rows:
                    id, name, tixa_url = row

                    # tixa_url match: success
                    if tixa_url == place_tixa_url: 
                        status = "success"
                        description = "Letezik az adatbazisban."
                        link = f"https://www.tivornya.hu/P/{id}"
                        break
                    # name match: partial success
                    elif tixa_url is None: 
                        status = "normal"
                        description = f"Letezik helyszin hasonlo nevvel ({name}). Nincs tixa_url-el osszekotve."
                        link = place_tixa_url #f"https://www.tivornya.hu/P/{id}"
                
                data = Data(
                    title=place_name,
                    description=description if description else "",
                    link=link,
                    status=status
                )
                
                if show_success or status != "success": serialized.append(data)
            
            serialized.sort(key=lambda p: p.status)
            return serialized

        """
        Function to get distinct events from the scraped data.
        """
        def events() -> list[list]:
            seen = set()
            unique_pairs = []

            for single in result:
                _, _, event_name, event_tixa_url, _ = single
                t = (event_name, event_tixa_url)
                if t not in seen:
                    seen.add(t)
                    unique_pairs.append([event_name, event_tixa_url])
            unique_pairs[:] = [pair for pair in unique_pairs if 'bérlet' not in pair[0].lower()]
            return unique_pairs

        def eval_events() -> list[Data]:
            scraped_events = events()

            serialized = []
            for event in scraped_events:
                event_name, event_tixa_url = event

                query = sql.SQL("""
                                SELECT event.id, event.name, url.tixa_url
                                FROM urls url
                                JOIN events event ON event.id = url.event_id
                                WHERE url.tixa_url = %s OR event.name LIKE %s;
                            """)

                cursor.execute(query, (event_tixa_url, event_name))
                rows = cursor.fetchall()

                status = "fail"
                description = "Az esemény nem talalhato az adatbazisban."
                link = event_tixa_url
                # link = f"https://www.facebook.com/search/events/?q={event_name}"
                for row in rows:
                    id, name, tixa_url = row

                    # tixa_url match: success
                    if tixa_url == event_tixa_url: 
                        status = "success"
                        description = "Letezik az adatbazisban."
                        link = f"https://www.tivornya.hu/E/{id}"
                        # link = f"https://www.facebook.com/search/events/?q={event_name}"
                        break
                    # name match: partial success
                    elif tixa_url is None: 
                        status = "normal"
                        description = f"Letezik esemény hasonlo nevvel ({name}). Nincs tixa_url-el osszekotve."
                        link = f"https://www.tivornya.hu/E/{id}"
                        # link = f"https://www.facebook.com/search/events/?q={event_name}"
                
                data = Data(
                    title=event_name,
                    description=description if description else "",
                    link=link,
                    status=status
                )
                
                if show_success or status != "success": serialized.append(data)
            
            serialized.sort(key=lambda p: p.status)
            return serialized

        pdf_data = [
            Title("Helyszínek"), 
            *eval_places(),
            Title("Események"),
            *eval_events()
        ]

        # event_in_database() + place_not_in_databese ()
        pdf = PDFData("Tixa Riport", date.today())
        pdf.set(pdf_data)
        pdf.create(filename=filename)

if __name__ == "__main__":
    # Init logging.
    logger = CustomLogger("TixaReport")
    logger.info("Starting...")

    DB_CONFIG = {
        "dbname": getenv("POSTGRES_DB", "mock"),
        "user": getenv("POSTGRES_USER", "user"),
        "password": getenv("POSTGRES_PASSWORD", "password"),
        "host": getenv("POSTGRES_HOST", "localhost"),
        "port": getenv("POSTGRES_PORT", 5432),
    }

    show_success = getenv("SHOW_SUCCESS", False)

    reporter = TixaConnector(DB_CONFIG)
    reporter.make_report(show_success=show_success)

    logger.info("Exiting...")
