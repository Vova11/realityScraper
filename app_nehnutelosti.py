import requests
import logging
from typing import List
from pydantic import ValidationError
from pages.nehnutelnosti_property_page import NehnutelnostiPropertyPage
from db.db import SessionLocal, Property
from pages.property_page import PropertyPage
from models.property import PropertySchema
from utils.helper_parse_funcs import filter_and_insert_new_properties, get_existing_property_ids, parse_properties_from_page, remove_duplicate_properties

session = SessionLocal()

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
    level=logging.DEBUG,
    filename="logs.txt",
)

logger = logging.getLogger("scraping")

logging.info("Loading nehnutelnosti listing...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}
base_url = "https://www.nehnutelnosti.sk/vysledky/predaj?locations=0_i9128BtwC-IGpZQrnK&locations=100010154&locations=100010662&locations=100010654&locations=100010131&locations=100010113&locations=100010001&locations=100010426&locations=DnC4128B1D1qP4jjZK1f&locations=100010555&locations=100010651&locations=100001042&categories=11&categories=300000&categories=15&categories=16&categories=12&categories=17&categories=18&categories=300001&categories=14&categories=200000&categories=400000&categories=400003&categories=400001&categories=400002&categories=400004&categories=400005&categories=200001&categories=500000&categories=500002&categories=500003&categories=500004&categories=500006&categories=500001"

def fetch_properties(url: str, headers: dict, session) -> tuple[list[dict], int]:
    page_content = requests.get(url, headers=headers).content
    first_page = NehnutelnostiPropertyPage(page_content)

    all_properties: List[dict] = []
    skipped_count = 0

    all_properties = parse_properties_from_page(first_page, url)

    #fetch next pages
    for page_num in range(2, first_page.page_count + 1):
        page_url = f"{url}&page={page_num}"
        print(f"Fetching page {page_num} from {page_url}...")
        page_content = requests.get(page_url, headers=headers).content
        current_page = NehnutelnostiPropertyPage(page_content)
        all_properties.extend(parse_properties_from_page(current_page, url))
        
    # Remove Duplicates
    unique_properties = remove_duplicate_properties(all_properties)
    # Get existing properties' IDs from DB
    existing_property_ids = get_existing_property_ids(session)

    # Filter new properties and add them to DB
    new_properties, skipped_count = filter_and_insert_new_properties(
        unique_properties, existing_property_ids, session
    )
    return unique_properties, skipped_count


def main():
    try:
        all_unique_properties, skipped_count = fetch_properties(base_url, headers, session)
        print(all_unique_properties)
        print(f"Skipped {skipped_count} properties")
        print(f"Total unique properties: {len(all_unique_properties)}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()