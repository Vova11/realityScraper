from bs4 import BeautifulSoup
import logging
import re
from locators.property_page_locators import PropertyPageLocators, NehnutelnostiPageLocators
from parsers.property import PropertyParser

logger = logging.getLogger('scraping.all_property_pages_topreality')

class PropertyPage:
    def __init__(self, page):
        logger.debug('Parsing page content topreality.sk')
        self.soup = BeautifulSoup(page, 'html.parser')
    
    @property
    def properties(self):
        logger.debug(f'Finding all properties in the {PropertyPageLocators.PROPERTY}.')
        locator = PropertyPageLocators.PROPERTY
        property_tags = self.soup.select(locator)
        return [ PropertyParser(e) for e in property_tags ]
    
    @property
    def page_count(self):
        logger.debug('Finding last page number')
        last_page_number = self.soup.select_one(PropertyPageLocators.PAGER).string
        logger.debug(f'Extracted number of pages as integer `{last_page_number}`.')
        return int(last_page_number)
    
    @property
    def type_of_sale(self):
        first_h1 = self.soup.select_one(PropertyPageLocators.TYPE_OF_SALE)
        if first_h1 and not None:
            res = first_h1.get_text(strip=True).split()
            listOfWords = {'predám': 'sale', 'predaj': 'sale', 'predať': 'sale',
                        'kúpa': 'buy', 'prenájom': 'rent'}  # Dictionary mapping

            # Check if second word exists and map it to the corresponding value
            result = listOfWords.get(res[1], "") if len(res) > 1 else ""

            return result
        
    @classmethod
    def get_type_of_sale_from_url(cls, url):
        match = re.search(r"/vysledky/([^/?]+)", url)  # Extracts the type from URL
        type_of_sale = match.group(1) if match else None

        # Map Slovak terms to English equivalents
        type_mapping = {
            "predaj": "sale",
            "prenajom": "rent"
        }

        return type_mapping.get(type_of_sale, None)  # Return mapped value or None


        


