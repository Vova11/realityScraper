from bs4 import BeautifulSoup
import logging
import re
from locators.property_page_locators import NehnutelnostiPageLocators
from parsers.nehnutelnosti_parser import NehnutelnostiParser

logger = logging.getLogger('scraping.all_property_pages_nehnutelnosti')

class NehnutelnostiPropertyPage:
    def __init__(self, page):
        logger.debug('Parsing page content of nehnutelnosti.sk')
        self.soup = BeautifulSoup(page, 'html.parser')
    
    @property
    def properties(self):
        logger.debug(f'Finding all properties in the {NehnutelnostiPageLocators.PROPERTY}.')
        locator = NehnutelnostiPageLocators.PROPERTY
        property_tags = self.soup.find_all('div', class_=locator)
        return [ NehnutelnostiParser(e) for e in property_tags ]
    
    @property
    def page_count(self):
        logger.debug('Finding last page number')
        last_li = self.soup.select_one(NehnutelnostiPageLocators.PAGER)
        return int(last_li.get_text(strip=True))
    
    @classmethod
    def get_type_of_sale_from_url(cls, url):
        match = re.search(r"/vysledky/([^/?]+)", url)
        type_of_sale = match.group(1) if match else None

        # Map Slovak terms to English equivalents
        type_mapping = {
            "predaj": "sale",
            "prenajom": "rent"
        }

        return type_mapping.get(type_of_sale, None) 
        

