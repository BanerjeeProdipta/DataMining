from bs4 import BeautifulSoup
import requests
import time

URL = "https://www.amazon.ca/s?k=dress&crid=VKRKZKECAD5U&sprefix=dress%2Caps%2C114&ref=nb_sb_noss_1"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

def fetch_page(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            return response.content
        except requests.exceptions.Timeout:
            print(f"Timeout occurred. Retrying... ({attempt + 1}/{retries})")
            time.sleep(delay)  # Wait before retrying
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break  # Break on other request-related errors
    return None  # Return None if all retries fail

page_content = fetch_page(URL)

if page_content:
    soup = BeautifulSoup(page_content, "html.parser")
    products = soup.find_all("div", class_="a-section a-spacing-base a-text-center")

    for product in products:
        # Get info from product object  
        title = product.h2.text.strip() if product.h2 else "No title available"
        link = product.a['href'] if product.a else "No link available"
        
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
    print("Failed to retrieve page content after multiple attempts.")
