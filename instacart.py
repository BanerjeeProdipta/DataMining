from bs4 import BeautifulSoup
import requests
import csv

def get_soup(url, headers):
    """Get the BeautifulSoup object for a given URL."""
    page = requests.get(url, headers=headers)
    return BeautifulSoup(page.content, "html.parser")

def extract_product_title(product):
    """Extract the title of the product."""
    title_tag = product.find("p", class_="e-1hrm03u")
    return title_tag.text if title_tag else "No title available"

def extract_product_price(product):
    """Extract the price of the product."""
    price_tag = product.find("p", class_="e-1lb6en9")
    return price_tag.text if price_tag else "Price not available"

def extract_product_data(product):
    """Extract the relevant product data (title and price)."""
    title = extract_product_title(product)
    price = extract_product_price(product)
    return [title, price]

def scrape_products_from_page(url, headers):
    soup = get_soup(url, headers)
    print('SOUP',soup)
    # Step 1: Find the <ul> element
    ul_element = soup.find("ul", class_="e-17mrx6g")

    if ul_element:
        # Step 2: Find all product items within the <ul>
        product_buttons = ul_element.find_all("button", class_="e-ecdxmw")
        product_data = [extract_product_data(product) for product in product_buttons]
        print('product_data',product_data)
        return product_data
    else:
        print("NOT FOUND!!")
        return []

def write_products_to_csv(filename, url, headers):
    """Scrape products from a single page and write to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Price"])

        print(f"Scraping the page...\n")
        products_data = scrape_products_from_page(url, headers)

        for product_data in products_data:
            writer.writerow(product_data)
            print(product_data)

# User-agent headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

# URL of the page to scrape
url = "https://www.instacart.ca/store/s?k=grocaries&search_source=logged_out_home_cross_retailer_search&search_id=dcad0c19-d1b2-4ef0-8f42-6634cc969cd6&page_view_id=52d1fe9a-7c42-5cb8-b33a-cbd4845b22a2"

# Scrape products from the page and write to CSV
write_products_to_csv("instacart.csv", url, headers)

print("Data has been successfully written to instacart.csv.")
