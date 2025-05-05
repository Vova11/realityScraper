import requests
from pages.property_page import PropertyPage

page_content = requests.get("https://www.topreality.sk/vyhladavanie-nehnutelnosti.html?form=1&type%5B%5D=102&type%5B%5D=103&type%5B%5D=104&type%5B%5D=105&type%5B%5D=106&obec=d101-Okres+Bratislava+I%2Cd102-Okres+Bratislava+II%2Cd103-Okres+Bratislava+III%2Cd104-Okres+Bratislava+IV%2Cd105-Okres+Bratislava+V&searchType=string&distance=&q=&cena_od=&cena_do=&vymera_od=0&vymera_do=0&n_search=search&page=estate&gpsPolygon=").content

page = PropertyPage(page_content)

properties = page.properties
    

   
def print_properties_by_price():
    sortByPrice = sorted(properties, key= lambda x: x.get_price)
    for p in sortByPrice:
        print(p)

property_generator = (x for x in properties)

def get_next_property():
    print(next(property_generator))
    

USER_CHOICE = '''Enter one of the following
- 'a' sortb by price
- 'b' just get next in catalogue
- 'q' quit
'''

def menu():
    user_input = input(USER_CHOICE)
    while user_input != 'q':
        if user_input == 'a':
            print_properties_by_price()
        elif user_input == 'b':
            get_next_property()
        else:
            print('Please choose valid command')
        user_input = input(USER_CHOICE)
    
    
menu()