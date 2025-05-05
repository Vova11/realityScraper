import requests
import logging
import json
from typing import List
from pydantic import ValidationError
from pages.property_page import PropertyPage
from db.db import SessionLocal, Property
from models.property import PropertySchema

session = SessionLocal()

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
    level=logging.DEBUG,
    filename="logs.txt",
)

logger = logging.getLogger("scraping")

logging.info("Loading topreality listing...")

base_url = "https://www.topreality.sk/vyhladavanie-nehnutelnosti.html?form=1&type%5B%5D=101&type%5B%5D=108&type%5B%5D=102&type%5B%5D=103&type%5B%5D=104&type%5B%5D=105&type%5B%5D=106&type%5B%5D=109&type%5B%5D=110&type%5B%5D=107&type%5B%5D=113&type%5B%5D=204&type%5B%5D=205&type%5B%5D=208&type%5B%5D=211&type%5B%5D=212&type%5B%5D=213&type%5B%5D=214&type%5B%5D=401&type%5B%5D=402&type%5B%5D=403&type%5B%5D=404&type%5B%5D=405&type%5B%5D=406&type%5B%5D=407&type%5B%5D=408&type%5B%5D=410&type%5B%5D=411&type%5B%5D=301&type%5B%5D=302&type%5B%5D=303&type%5B%5D=304&type%5B%5D=305&type%5B%5D=306&type%5B%5D=307&type%5B%5D=308&type%5B%5D=309&type%5B%5D=310&type%5B%5D=311&type%5B%5D=312&type%5B%5D=313&type%5B%5D=314&type%5B%5D=315&type%5B%5D=316&type%5B%5D=317&type%5B%5D=319&type%5B%5D=320&type%5B%5D=321&type%5B%5D=322&type%5B%5D=324&type%5B%5D=323&type%5B%5D=331&type%5B%5D=801&type%5B%5D=802&type%5B%5D=803&type%5B%5D=806&type%5B%5D=807&type%5B%5D=809&type%5B%5D=810&type%5B%5D=811&type%5B%5D=812&type%5B%5D=813&type%5B%5D=814&type%5B%5D=815&type%5B%5D=816&type%5B%5D=818&type%5B%5D=819&type%5B%5D=820&type%5B%5D=821&obec=c100-Bratislavsk%C3%BD+kraj%2C103%2C95%2Ccp95-1-Al%C5%BEbetin+Dvor%2C207&searchType=string&distance=&q=&cena_od=&cena_do=&vymera_od=0&vymera_do=0&n_search=search&page=estate&gpsPolygon="

def fetch_properties(url: str, session) -> tuple[list[dict], int]:
    """
    Fetches properties from topreality.sk, handles pagination, and manages database operations.

    Args:
        url: The base URL of the property listing.
        session: SQLAlchemy session.

    Returns:
        A tuple containing:
        - A list of unique property dictionaries.
        - The count of properties skipped due to existing in DB or validation errors.
    """
    page_content = requests.get(url).content
    first_page = PropertyPage(page_content)

    all_properties: List[dict] = []
    skipped_count = 0

    # Add first page to list
    for property_obj in first_page.properties:
        try:
            property_data = {
                "id": property_obj.id,
                "title": property_obj.name,
                "price": property_obj.price,
                "price_per_meter": property_obj.price_per_meter,
                "area": property_obj.area,
                "street": property_obj.address,
                "city": property_obj.city,
                "district": property_obj.district,
                "affiliation": property_obj.afiliation,
                "type": property_obj.category2,
                "rooms": property_obj.rooms,
                "url": property_obj.url,
                "category": property_obj.category,
                "website": "topreality",
                "typeOfSale": first_page.type_of_sale,
                "owner_id": 1
            }
            all_properties.append(property_data)
        except (ValidationError, AttributeError) as ex:  #catching ValidationError from pydantic and AttributeError from the page
            print(f"Skipping property due to error: {ex}")
            print(property_obj.name)
            skipped_count +=1
            

    # Fetch next pages
    for page_num in range(2, first_page.page_count + 1):
        
        page_url = f"https://www.topreality.sk/vyhladavanie-nehnutelnosti-{page_num}.html?form=1&type%5B%5D=101&type%5B%5D=108&type%5B%5D=102&type%5B%5D=103&type%5B%5D=104&type%5B%5D=105&type%5B%5D=106&type%5B%5D=109&type%5B%5D=110&type%5B%5D=107&type%5B%5D=113&type%5B%5D=204&type%5B%5D=205&type%5B%5D=208&type%5B%5D=211&type%5B%5D=212&type%5B%5D=213&type%5B%5D=214&type%5B%5D=401&type%5B%5D=402&type%5B%5D=403&type%5B%5D=404&type%5B%5D=405&type%5B%5D=406&type%5B%5D=407&type%5B%5D=408&type%5B%5D=410&type%5B%5D=411&type%5B%5D=301&type%5B%5D=302&type%5B%5D=303&type%5B%5D=304&type%5B%5D=305&type%5B%5D=306&type%5B%5D=307&type%5B%5D=308&type%5B%5D=309&type%5B%5D=310&type%5B%5D=311&type%5B%5D=312&type%5B%5D=313&type%5B%5D=314&type%5B%5D=315&type%5B%5D=316&type%5B%5D=317&type%5B%5D=319&type%5B%5D=320&type%5B%5D=321&type%5B%5D=322&type%5B%5D=324&type%5B%5D=323&type%5B%5D=331&type%5B%5D=801&type%5B%5D=802&type%5B%5D=803&type%5B%5D=806&type%5B%5D=807&type%5B%5D=809&type%5B%5D=810&type%5B%5D=811&type%5B%5D=812&type%5B%5D=813&type%5B%5D=814&type%5B%5D=815&type%5B%5D=816&type%5B%5D=818&type%5B%5D=819&type%5B%5D=820&type%5B%5D=821&obec=c100-Bratislavsk%C3%BD+kraj%2C103%2C95%2Ccp95-1-Al%C5%BEbetin+Dvor%2C207&searchType=string&distance=&q=&cena_od=&cena_do=&vymera_od=0&vymera_do=0&n_search=search&page=estate&gpsPolygon="
        print(f"Fetching page {page_num} from {page_url}...")
        page_content = requests.get(page_url).content
        current_page = PropertyPage(page_content)

        for property_obj in current_page.properties:
             try:
                property_data = {
                    "id": property_obj.id,
                    "title": property_obj.name,
                    "price": property_obj.price,
                    "price_per_meter": property_obj.price_per_meter,
                    "area": property_obj.area,
                    "street": property_obj.address,
                    "city": property_obj.city,
                    "district": property_obj.district,
                    "affiliation": property_obj.afiliation,
                    "type": property_obj.category2,
                    "rooms": property_obj.rooms,
                    "url": property_obj.url,
                    "category": property_obj.category,
                    "website": "topreality",
                    "typeOfSale": current_page.type_of_sale,
                    "owner_id": 1
                }
                all_properties.append(property_data)
             except (ValidationError, AttributeError) as ex:  #catching ValidationError from pydantic and AttributeError from the page
                print(f"Skipping property due to error: {ex}")
                print(property_obj.name)
                skipped_count +=1
                
    # Remove Duplicates
    unique_properties = remove_duplicate_properties(all_properties)
    # Get existing properties' IDs from DB
    existing_property_ids = get_existing_property_ids(session)

    # Filter new properties and add them to DB
    new_properties, skipped_from_db_count = filter_and_insert_new_properties(
        unique_properties, existing_property_ids, session
    )
    return unique_properties, skipped_count + skipped_from_db_count


def remove_duplicate_properties(property_list: list[dict]) -> list[dict]:
    """Removes duplicate properties from a list based on property_id."""
    unique_properties: List[dict] = []
    seen_property_ids = set()
    for item in property_list:
        property_id = str(item["id"])
        if property_id not in seen_property_ids:
            seen_property_ids.add(property_id)
            unique_properties.append(item)
    return unique_properties


def get_existing_property_ids(session) -> set:
    """Fetches existing property IDs from the database."""
    return set(str(i[0]) for i in session.query(Property.property_id).all())


def filter_and_insert_new_properties(
    properties: list[dict], existing_ids: set, session
) -> tuple[list, int]:
    """Filters out existing properties and inserts new ones into the database."""
    new_properties = []
    skipped_count = 0
    batch_size = 500
    batch_counter = 0
    for item in properties:
        item_property_id = str(item["id"])
        if item_property_id in existing_ids:
            print(f"Skipping property: {item_property_id} (Already exists)")
            skipped_count += 1
        else:
            print(f"Inserting new property: {item_property_id}")
            new_property = Property(
                property_id=item.get('id'),
                title=item.get('title'),
                street=item.get('street'),
                city=item.get('city'),
                district=item.get('district'),
                area=item.get('area'),
                affiliation=item.get('affiliation'),
                price=item.get('price'),
                category=item.get('category'),
                typeApt=item.get('type'),
                rooms=item.get('rooms'),
                url=item.get('url'),
                price_per_meter=item.get('price_per_meter'),
                website="topreality",
                parsed=True,
                typeOfSale=item.get('typeOfSale'),
                owner_id=item.get('owner_id')
            )
            new_properties.append(new_property)
            batch_counter += 1

            if batch_counter % batch_size == 0:  # ✅ Commit every 500 records
                session.bulk_save_objects(new_properties)  # Bulk insert
                session.commit()  # Commit batch
                new_properties.clear()  # Clear list for next batch
                print(f"✅ Committed batch of {batch_size} properties.")

    if new_properties:
        session.bulk_save_objects(new_properties)
        session.commit()
        print(f"✅ Committed final batch of {len(new_properties)} properties.")
    else:
        print("No new properties to insert.")

    return new_properties, skipped_count


def main():
    try:
        all_unique_properties, skipped_count = fetch_properties(base_url, session)

        print(f"Skipped {skipped_count} properties")
        print(f"Total unique properties: {len(all_unique_properties)}")
        #print(json.dumps(all_unique_properties, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()