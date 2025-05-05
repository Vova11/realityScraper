from typing import List, Tuple
from db.db import Property
from models.property import PropertySchema
from pages.property_page import PropertyPage
from pydantic import ValidationError

def parse_properties_from_page(page, url) -> List[dict]:
    properties = []
    for property_obj in page.properties:
        try:
            property_data = PropertySchema(
                property_id=property_obj.id,
                title=property_obj.name,
                price=property_obj.price,
                description=property_obj.description,
                price_per_meter=property_obj.price_per_meter,
                area=property_obj.address.get('area'),
                street=property_obj.address.get('street'),
                city=property_obj.address.get('city'),
                district=property_obj.address.get('district'),
                affiliation=property_obj.affiliation,
                typeApt=property_obj.address.get('type'),
                rooms=property_obj.address.get('rooms'),
                url=property_obj.url,
                typeOfSale=PropertyPage.get_type_of_sale_from_url(url)
            )
            properties.append(property_data.model_dump())
        except ValidationError as ex:
            print(f"Skipping property due to validation error: {ex}")
            print(property_obj.name)
    return properties


def remove_duplicate_properties(property_list: list[dict]) -> list[dict]:
    """Removes duplicate properties from a list based on property_id."""
    unique_properties: List[dict] = []
    seen_property_ids = set()
    for item in property_list:
        property_id = str(item["property_id"])
        if property_id not in seen_property_ids:
            seen_property_ids.add(property_id)
            unique_properties.append(item)
    return unique_properties


def get_existing_property_ids(session) -> set:
    return set(
        str(i[0]) for i in session.query(Property.property_id).all()
    )
    

def filter_and_insert_new_properties(
    properties: List[dict], existing_ids: set, session
) -> Tuple[List, int]:
    """Filters out existing properties and inserts new ones into the database."""
    new_properties = []
    skipped_count = 0
    for item in properties:
        item_property_id = str(item["property_id"])
        if item_property_id in existing_ids:
            print(f"Skipping property: {item_property_id} (Already exists)")
            skipped_count += 1
        else:
            print(f"Inserting new property: {item_property_id}")
            new_properties.append(Property(**item))

    if new_properties:
        session.add_all(new_properties)
        session.commit()
        print(f"Inserted {len(new_properties)} new properties")
    else:
        print("No new properties to insert.")
    return new_properties, skipped_count
    