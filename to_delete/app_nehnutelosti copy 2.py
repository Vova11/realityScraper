import logging
import requests
import psycopg2
from pages.nehnutelnosti_property_page import NehnutelnostiPropertyPage

# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', 
    datefmt='%d-%m-%y %H:%M:%S',
    level=logging.DEBUG,
    filename='logs.txt'
)

logger = logging.getLogger('scraping')
logger.info('Loading nehnutelnosti listing...')

# Database connection details
DB_CONFIG = {
    'dbname': 'realestate',
    'user': 'postgres',
    'password': 'your_password_here',  # Replace with your PostgreSQL password
    'host': 'localhost',
    'port': '5432'
}

# Function to save data to PostgreSQL
def save_to_db(property_data):
    try:
        # Establish the connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert query with conflict handling to avoid duplicates
        insert_query = """
            INSERT INTO properties (
                property_id, title, price, area, street, city, district, 
                affiliation, type, url, category, price_per_meter, website
            ) VALUES (
                %(property_id)s, %(title)s, %(price)s, %(area)s, %(street)s, 
                %(city)s, %(district)s, %(affiliation)s, %(type)s, %(url)s, 
                %(category)s, %(price_per_meter)s, %(website)s
            ) ON CONFLICT (url) DO NOTHING;
        """
        
        # Execute the query and commit
        cursor.execute(insert_query, property_data)
        conn.commit()
        
        logger.info(f"Saved property to DB: {property_data['title']}")
    
    except Exception as e:
        logger.error(f"Error saving to DB: {e}")
    
    finally:
        cursor.close()
        conn.close()

# Initialize property_list outside the loop to accumulate results
property_list = []

# Loop through the pages
for page_num in range(1, 5):
    url = f"https://www.nehnutelnosti.sk/vysledky/bratislava-ruzinov/predaj?categories=11&categories=12&categories=300001&categories=14&categories=15&categories=16&categories=17&categories=18&page={page_num}"
    logger.debug(f"Fetching page {page_num}: {url}")
    
    page_content = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }).content
    logger.debug('Creating PropertyPage from content of nehnutelnosti.sk')
    
    # Parse the page content
    page = NehnutelnostiPropertyPage(page_content)
    properties = page.properties
    
    current_page_list = []

    for property_obj in properties:
        property_dict = {
            "property_id": property_obj.id,
            "title": property_obj.name,
            "price": property_obj.price,
            "area": property_obj.address.get('area'),
            "street": property_obj.address.get('street'),
            "city": property_obj.address.get('city'),
            "district": property_obj.address.get('district'),  # Fixed typo from 'disctrict'
            "affiliation": property_obj.affiliation,
            "type": property_obj.address.get('type'),
            "url": property_obj.url,
            "category": "",
            "price_per_meter": property_obj.price_per_meter,
            "website": "nehnutelnosti.sk",
        }
        current_page_list.append(property_dict)
    
    property_list.extend(current_page_list)
    logger.debug(f"Added {len(current_page_list)} properties from page {page_num}")

    # Save current page's properties to the database
    for property_data in current_page_list:
        save_to_db(property_data)

logger.info(f"Total properties collected: {len(property_list)}")
print(len(property_list))
