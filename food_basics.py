import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def initialize_driver(url):
    """Initialize the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.set_window_size(1200, 900)
    print(driver.title)
    return driver


def click_next_page_button(driver):
    """Click the 'Next page' button to load additional products."""
    try:
        # Wait for the next button to be clickable based on class and aria-label
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ppn--element.corner[aria-label='Next']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(2)  # Allow UI to settle
        driver.execute_script("arguments[0].click();", next_button)
        print('"Next page" button clicked.')
        return True
    except Exception as e:
        print(f"Failed to click the 'Next page' button: {e}")
        return False

def scrape_data(html):
    """Extract product data (title and price) from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")

    # Find the div with class 'products-search--grid searchOnlineResults'
    product_grid = soup.find("div", class_="products-search--grid searchOnlineResults")
    
    if product_grid:
        # Find all individual products with class 'default-product-tile tile-product item-addToCart'
        product_items = product_grid.find_all("div", class_="default-product-tile tile-product item-addToCart")
        products = []
        
        for product in product_items:
            product_info = {
                "Title": extract_product_title(product),
                "Price": extract_product_price(product),
            }
            products.append(product_info)
        
        return products
    else:
        return []


def extract_product_title(product):
    """Extract the product title from the product container."""
    title_tag = product.find("div", class_="head__title")  
    return title_tag.text.strip() if title_tag else "No title available"


def extract_product_price(product):
    """Extract the product price from the product container."""
    price_tag = product.find("span", class_="price-update")  
    return price_tag.text.strip() if price_tag else "Price not available"


def write_csv(dataframe, file_name):
    """Write the DataFrame to a CSV file."""
    dataframe.to_csv(f"{file_name}.csv", index=False)


def main():
    url = "https://www.foodbasics.ca/search?filter=groceries"
    
    # Initialize the driver
    driver = initialize_driver(url)
    
    # Hold all scraped products
    all_products = []
    
    # Click the 'Next page' button up to 10 times, or until it no longer appears
    max_clicks = 10
    for _ in range(max_clicks):
        time.sleep(5)  # Give time for the page to load fully after each click
        
        # Scrape the current page's products
        html = driver.page_source
        products = scrape_data(html)
        all_products.extend(products)  # Append all products from the current page
        
        # Try to click the 'Next page' button
        if not click_next_page_button(driver):
            print("No more 'Next page' button found, stopping.")
            break
    
    # Quit the driver after scraping
    driver.quit()
    
    # Create a DataFrame and write to a CSV
    if all_products:
        product_df = pd.DataFrame(all_products)
        write_csv(product_df, "foodbasics_products")
        print("Web Scraping and CSV file writing complete!")
    else:
        print("No products were scraped.")


if __name__ == "__main__":
    main()
