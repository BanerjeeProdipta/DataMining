import requests
from bs4 import BeautifulSoup

# Set the URL for Best Buy search (change query as needed)
url = "https://www.bestbuy.com/site/searchpage.jsp?st=laptop"

# Headers to simulate a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
}

# Send a GET request to Best Buy
response = requests.get(url, headers=headers)


# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    print(soup)

    # Find all the product containers on the page
    products = soup.find_all("li", class_="sku-item")

    # Loop through each product container and extract the data
    for product in products:
        # Extract product name
        product_name_tag = product.find("h4", class_="sku-header")
        product_name = product_name_tag.text.strip() if product_name_tag else "No name"

        # Extract product link
        product_link_tag = product_name_tag.find("a")
        product_link = (
            "https://www.bestbuy.com" + product_link_tag["href"]
            if product_link_tag
            else "No link"
        )

        # Extract product price
        price_tag = product.find(
            "div", class_="priceView-hero-price priceView-customer-price"
        )
        price = (
            price_tag.find("span").text.strip() if price_tag else "Price not available"
        )

        # Print the extracted data
        print(f"Product Name: {product_name}")
        print(f"Product Link: {product_link}")
        print(f"Price: {price}")
        print("-" * 50)
else:
    print(f"Failed to retrieve page content. Status code: {response.status_code}")
