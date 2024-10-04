from bs4 import BeautifulSoup
import requests

url = "https://www.amazon.ca/s?k=laptop&crid=1WXLR37VMDX3P&sprefix=laptop%2Caps%2C109&ref=nb_sb_noss_1"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response, "html.parser")
    products = soup.find_all("div", class_="a-section a-spacing-base a-text-center")

    for product in products:
        # Get info from product object
        title = product.h2.text.strip() if product.h2 else "No title available"
        link = product.a["href"] if product.a else "No link available"

        if link:
            full_link = "https://www.amazon.ca" + link
        else:
            full_link = "No link available"

        price_whole = product.find("span", class_="a-price-whole")
        price_fraction = product.find("span", class_="a-price-fraction")

        if price_whole and price_fraction:
            price = price_whole.text + price_fraction.text
        else:
            price = "Price not available"

        # Print the extracted data
        print(f"Title: {title}")
        print(f"Link: {full_link}")
        print(f"Price: {price}")
        print("-" * 50)
else:
    print(f"Failed to retrieve page content. Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text preview: {response.text[:500]}")
