import logging
import requests
import psycopg2
from psycopg2.extras import execute_values
from pages.nehnutelnosti_property_page import NehnutelnostiPropertyPage

# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', 
    datefmt='%d-%m-%y %H:%M:%S',
    level=logging.DEBUG,
    filename='logs.txt'
)

url = f"https://www.nehnutelnosti.sk/vysledky/bratislava-ruzinov/predaj?categories=11&categories=12&categories=300001&categories=14&categories=15&categories=16&categories=17&categories=18"


page_content = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}).content


# Parse the page content
page = NehnutelnostiPropertyPage(page_content)
properties = page.properties

# Database connection details
DB_CONFIG = {
    'dbname': 'realestate',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Function to check if property_id exists in DB
def property_exists(property_id):
    conn = None
    cursor = None  # Initialize cursor as None
    
    try:
        # Establish the connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check for existence query
        check_query = """
            SELECT 1 FROM properties WHERE property_id = %s LIMIT 1;
        """
        
        # Execute the check query
        cursor.execute(check_query, (property_id,))
        result = cursor.fetchone()
        
        # Return True if found, False if not
        return result is not None
    
    except Exception as e:
        logger.error(f"Error checking existence in DB: {e}")
        return False
    
    finally:
        if cursor:
            cursor.close()
        
        if conn:
            conn.close()

# Function to save data to PostgreSQL in batches
def save_to_db_batch(property_batch):
    if not property_batch:
        return  # Exit if no data to insert

    conn = None
    try:
        # Establish the connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert query with conflict handling to avoid duplicates
        insert_query = """
            INSERT INTO properties (
                property_id, title, price, area, street, city, district, 
                affiliation, typeApt, url, category, price_per_meter, website
            ) VALUES %s
            ON CONFLICT (url) DO NOTHING;
        """
        
        # Prepare data for batch insert
        data_to_insert = [
            (
                property_data["property_id"],
                property_data["title"],
                property_data["price"],
                property_data["area"],
                property_data["street"],
                property_data["city"],
                property_data["district"],
                property_data["affiliation"],
                property_data["typeApt"],
                property_data["url"],
                property_data["category"],
                property_data["price_per_meter"],
                property_data["website"]
            )
            for property_data in property_batch
        ]
        
        # Execute batch insert
        execute_values(cursor, insert_query, data_to_insert)
        conn.commit()
        
        
    
    except Exception as e:
        pass
    
    finally:
        if cursor:
            cursor.close()
        
        if conn:
            conn.close()

# Initialize property_list outside the loop to accumulate results
property_list = []

# Loop through the pages
for page_num in range(1, 22):
    url = f"https://www.nehnutelnosti.sk/vysledky/bratislava-ruzinov/predaj?categories=11&categories=12&categories=300001&categories=14&categories=15&categories=16&categories=17&categories=18&page={page_num+1}"
    
    
    page_content = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }).content
    
    
    # Parse the page content
    page = NehnutelnostiPropertyPage(page_content)
    properties = page.properties
    
    current_page_list = []

    for property_obj in properties:
        # Check if property_id already exists
        if property_exists(property_obj.id):
            continue
        
        property_dict = {
            "property_id": property_obj.id,
            "title": property_obj.name,
            "price": property_obj.price,
            "area": property_obj.address.get('area'),
            "street": property_obj.address.get('street'),
            "city": property_obj.address.get('city'),
            "district": property_obj.address.get('district'),
            "affiliation": property_obj.affiliation,
            "typeApt": property_obj.address.get('type'),
            "url": property_obj.url,
            "category": "",
            "price_per_meter": property_obj.price_per_meter,
            "website": "nehnutelnosti.sk",
        }
        current_page_list.append(property_dict)
    
    property_list.extend(current_page_list)
    

    # Save properties in batch to the database
    save_to_db_batch(current_page_list)


print(len(property_list))
