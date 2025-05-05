import re
import logging
from typing import Optional
from locators.property_locators import PropertyLocators

logger = logging.getLogger('scraping.property_parser')

class PropertyParser:
    """
    find data for a property  in topreality
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.numOfRooms = ''
    
    
    def __repr__(self):
        return f'< title: {self.name} \n price: {self.price} >'
    
    
    @property
    def id(self) -> str:
        locator = PropertyLocators.ITEM_ID
        return self.parent.get(locator, None)
    
    @property
    def name(self) -> str:
        locator = PropertyLocators.ITEM_NAME
        return self.parent.get(locator, None)
    
    @property
    def address(self) -> str:
        locator = self.parent.select_one(PropertyLocators.ITEM_ADDRESS)
        text = locator.get_text(strip=True).rstrip(',') if locator else None
        return text
    
    @property
    def city(self) -> str:
        locator = self.parent.select_one(PropertyLocators.ITEM_CITY)
        text = locator.get_text(strip=True).rstrip(',') if locator else None
        return text
    
    @property
    def district(self) -> str:
        locator = self.parent.select_one(PropertyLocators.ITEM_DISTRICT)
        text = locator.get_text(strip=True).lstrip('(').rstrip(')') if locator else None
        return text
    
    

    @property
    def area(self) -> Optional[float]:
        locator = self.parent.select_one(PropertyLocators.ITEM_AREA)
        
        if locator is None:
            print("Warning: Area element not found!")
            return 0.0

        area_text = locator.get_text(strip=True)

        # ✅ Remove all possible variations of "m²", "m2", or extra spaces
        area_text = re.sub(r'\s*m[²2]$', '', area_text).strip()

        try:
            return float(area_text)
        except ValueError:
            print(f"Warning: Could not convert area to float: {area_text}")
            return 0.0

    @property
    def afiliation(self) -> str:
        locator = PropertyLocators.ITEM_AFFILIATION
        return self.parent.get(locator, None)
    
    @property
    def price(self) -> float:
        locator = PropertyLocators.ITEM_PRICE
        float_price = self.parent.get(locator, 0.00)
        return float(float_price)
    
    @property
    def currency(self) -> str:
        locator = PropertyLocators.ITEM_CURRENCY
        return self.parent.get(locator, None)
    
    @property
    def category(self) -> str:
        locator = PropertyLocators.ITEM_CATEGORY
        return self.parent.get(locator, None)
    
    @property
    def category2(self) -> str:
        locator = PropertyLocators.ITEM_CATEGORY2
        numOfRooms = self.parent.get(locator, None)
        self.numOfRooms = numOfRooms
        return numOfRooms
    
    @property
    def category3(self) -> str:
        locator = PropertyLocators.ITEM_CATEGORY3
        return self.parent.get(locator, None)
    
    @property
    def category4(self) -> str:
        locator = PropertyLocators.ITEM_CATEGORY4
        return self.parent.get(locator, None)
    
    @property
    def category5(self) -> str:
        locator = PropertyLocators.ITEM_CATEGORY5
        return self.parent.get(locator, None)
    
    @property
    def url(self):
        return self.parent.find('a').attrs['href']
    
    @property
    def price_per_meter(self) -> float:
        price_tag = self.parent.select_one('small.text-muted')
        
        if price_tag:
            price = price_tag.text.strip()
            price = price.replace(' ', '').replace(',', '.')[:-4]
            
            if price.replace('.', '', 2).isdigit():
                return float(price)
        return 0.00

    @property
    def type(self):
        return "other"
    
    @property
    def rooms(self):
        rooms = self.numOfRooms[:1] if self.numOfRooms else "other"
        return rooms
    
    