import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'dbname': 'realestate',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Dummy data to insert
dummy_data = {
    "property_id": "dummy123",
    "title": "Dummy Property",
    "price": 123456,
    "area": "100 m²",
    "street": "Dummy Street",
    "city": "Dummy City",
    "district": "Dummy District",
    "affiliation": "Dummy Affiliation",
    "type": "Apartment",
    "url": "https://dummyurl.com",
    "currency": "EUR",
    "category": "Dummy Category",
    "website": "dummywebsite.com"
}

# Insert query
insert_query = """
    INSERT INTO properties (
        property_id, title, price, area, street, city, district, 
        affiliation, type, url, currency, category, website
    ) VALUES (
        %(property_id)s, %(title)s, %(price)s, %(area)s, %(street)s, %(city)s, 
        %(district)s, %(affiliation)s, %(type)s, %(url)s, 
        %(currency)s, %(category)s, %(website)s
    )
    ON CONFLICT (url) DO NOTHING;
"""

def insert_dummy_data():
    try:
        # Establish the connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Execute the insert query
        cursor.execute(insert_query, dummy_data)
        conn.commit()
        
        print("Dummy data inserted successfully.")
    
    except Exception as e:
        print("Error:", e)
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    insert_dummy_data()
