import re
import logging
from typing import Optional, Dict, Union
from locators.property_locators import NehnutelnostiPropertyLocators

logger = logging.getLogger('scraping.property_parser')

class NehnutelnostiParser:
    """
    find data for a property  in nehnutelnosti
    """
    def __init__(self, parent):
        self.parent = parent
        
    def __repr__(self):
        return f'< title: {self.name} \n price: {self.price} >'
    
    @property
    def id(self) -> Optional[str]:
        url_tag = self.parent.find('a', class_=NehnutelnostiPropertyLocators.ITEM_URL)
        get_url = url_tag.get('href') if url_tag else None
        
        if get_url:
            # Pattern 1: /detail/<id>/
            pattern_detail = r'/detail/([A-Za-z0-9\-_]+)(?=[/-])'
            
            # Pattern 2: /developersky-projekt/<id>/
            pattern_dev_proj = r'/developersky-projekt/([A-Za-z0-9\-_]+)(?=[/-])'
            
            
            # Try matching each pattern in sequence
            match = re.search(pattern_detail, get_url)
            if match:
                print(f"Matched Pattern 1 (Detail): {get_url}")
                return match.group(1)
            
            match = re.search(pattern_dev_proj, get_url)
            if match:
                print(f"Matched Pattern 2 (Developersky Projekt): {get_url}")
                return match.group(1)
            
            # If no patterns matched
            print(f"No pattern matched for URL: {get_url}")
        
        return None

        
    @property
    def name(self) -> str:
        locator = NehnutelnostiPropertyLocators.ITEM_NAME
        title = self.parent.find('h2', class_=locator)
        return title.get_text(strip=True) if title else None
    
    @property
    def description(self) -> str:
        locator = NehnutelnostiPropertyLocators.ITEM_DESCRIPTION
        description = self.parent.find('p', class_=locator)
        return description.get_text(strip=True) if description else None
    
    @property
    def price(self) -> float:
        locator = NehnutelnostiPropertyLocators.ITEM_PRICE
        price = self.parent.find('p', class_=locator)

        if price:
            price_text = price.get_text(strip=True)
            price_text = price_text.replace('\xa0', '').replace('€', '').replace(',', '')
            cleaned_price = re.sub(r'[^\d.]', '', price_text)

            try:
                return float(cleaned_price)
            except ValueError:
                pass

        return 0.0 

    
        
    @property
    def price_per_meter(self) -> float:
        locator = NehnutelnostiPropertyLocators.ITEM_PRICE_PER_METER
        item_price_per_meter = self.parent.find('p', class_=locator)

        if item_price_per_meter:
            # Clean the text
            price_text = item_price_per_meter.get_text(strip=True)
            price_text = price_text.replace('\xa0', '').replace('€', '').replace(',', '.')
            
            # Extract only the numeric part (stopping at the first non-numeric character)
            cleaned_price = re.match(r'^[\d.]+', price_text)

            if cleaned_price:
                try:
                    return float(cleaned_price.group(0))
                except ValueError:
                    pass  # Skip error handling, return default below

        return 0.0  # Default value if parsing fails




    @property
    def address(self) -> Dict[str, Union[str, float]]:
        locator = NehnutelnostiPropertyLocators.ITEM_PROPERTY_ADDRESS_CITY_DISCTRICT_TYPE_AREA
        # Find all <p> tags matching the locator class
        address_tags = self.parent.find_all('p', class_=locator)
        
        # Extract and clean text from each tag
        address_parts = [tag.get_text(strip=True) for tag in address_tags]
        
        # Limit to first 5 elements (since we're expecting 5 parts)
        address_parts = address_parts[:5]
        
        # Pad with empty strings if fewer than 5 parts are found
        while len(address_parts) < 5:
            address_parts.append('')
        
        # Manually rearranging based on the pattern
        # Example pattern observed: 'Street, District, City', 'Type', 'Area'
        if len(address_parts) >= 3:
            street_part = address_parts[0].split(', ')
            if len(street_part) == 3:
                street, district, city = street_part
            else:
                street = address_parts[0]
                district = ''
                city = ''
            
            property_type = address_parts[1]
            rooms = property_type[:1] if property_type[:1] else "other"
            # Check if area is not empty before conversion
            area_text = address_parts[2].replace('m²', '').strip()

            # Check if area_text is a valid number before converting
            if area_text.replace('.', '', 1).isdigit():
                area = float(area_text)
            else:
                area = 0.00
        else:
            street, district, city, property_type, area = '', '', '', '', ''
        
        mapped_values = {
            'street': street,
            'district': district,
            'city': city,
            'type': property_type,
            'rooms': rooms,
            'area': area,
        }
        
        return mapped_values

    @property
    def affiliation(self) -> str:
        get_p = self.parent.select_one(NehnutelnostiPropertyLocators.ITEM_AFFILIATION)
        return get_p.get_text(strip=True) if get_p else None
    
    @property
    def url(self) -> str:
        url_tag = self.parent.find('a', class_=NehnutelnostiPropertyLocators.ITEM_URL)
        get_url = url_tag.get('href') if url_tag else None
        return get_url or None
    
    