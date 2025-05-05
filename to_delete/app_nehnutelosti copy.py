import requests
import logging
import json
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}
page_content = requests.get("https://www.nehnutelnosti.sk/vysledky/bratislava-ruzinov/predaj?categories=11&categories=12&categories=300001&categories=14&categories=15&categories=16&categories=17&categories=18", headers=headers).content
soup = BeautifulSoup(page_content, 'html.parser')

containers = soup.find_all('div', class_='MuiBox-root mui-1yjvs5a')

for container in containers:
    # Extracting MuiTypography-root 2
    title = container.find('h2', class_='MuiTypography-h4')
    
    description = container.find('p', class_='MuiTypography-body2')
    price = container.find('p', class_='MuiTypography-h5')
    price_per_meter = container.find('p', class_='MuiTypography-label1')
    # Check if the title exists and extract text
    if title:
        print("Title:", title.text.strip())
    else:
        print("Title not found.")
    
    # Extracting all p tags with class MuiTypography-body3
    address = container.find_all('p', class_='MuiTypography-body3')
    
    
    # Check if at least 1 <p> is present
    if len(address) > 0:
        first_p = address[0].text.strip()
        print("Address:", first_p)
    else:
        print("First P: Not available")
    
    # Check if at least 2 <p> tags are present
    if len(address) > 1:
        second_p = address[1].text.strip()
        print("type:", second_p)
    else:
        print("Second P: Not available")
    
    # Check if at least 3 <p> tags are present
    if len(address) > 2:
        third_p = address[2].text.strip()
        print("area:", third_p)
    else:
        print("Third P: Not available")
    
    if price:
        print(price.text.strip())
    
    if price_per_meter:
        print(price_per_meter.text.strip())