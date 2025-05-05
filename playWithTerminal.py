print('HI')
response = input("Do you want to start shopping? y/n \n")

products = {
    'A': {
        'price': 200
    },
    'B': {
        'price': 300   
    }
}
if response.lower() == "y":
    print("lets do shopping")
    print("choose from products")
    for name, details in products.items():
        print(f"{name} - {details['price']}")
    for key in products.keys():
        print("Key:", key)
    product = input("Choose product: ")
    if product in products:
        quantity = int(input("Enter quantity: "))
        total_price = products[product]['price'] * quantity
        print(f"Total price for {quantity} {product} is {total_price}")
    else:
        print("Invalid product")
elif response.lower() == "n":
    print("See you later")
elif response.lower() == "exit":
    print("Bye")
elif response.lower() == "q":
    print("Bye")
elif response.lower() == "quit":
    print("Bye")

    