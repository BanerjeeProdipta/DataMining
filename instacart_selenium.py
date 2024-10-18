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
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next page']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(2)  # Allow UI to settle
        driver.execute_script("arguments[0].click();", next_button)
        print('"Next page" button clicked.')
        return True
    except Exception as e:
        print(f"Failed to click the 'Next page' button: {e}")
        return False


def scrape_instacart_data(html):
    """Extract product data (title and price) from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")

    # Find the <ul> element with the class 'e-17mrx6g'
    ul_element = soup.find("ul", class_="e-17mrx6g")
    
    if ul_element:
        # Find all product items within the <ul>
        product_buttons = ul_element.find_all("button", class_="e-ecdxmw")
        products = []
        
        for product in product_buttons:
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
    title_tag = product.find("p", class_="e-1hrm03u")
    return title_tag.text if title_tag else "No title available"


def extract_product_price(product):
    """Extract the product price from the product container."""
    price_tag = product.find("p", class_="e-1lb6en9")
    return price_tag.text if price_tag else "Price not available"


def write_csv(dataframe, file_name):
    """Write the DataFrame to a CSV file."""
    dataframe.to_csv(f"{file_name}.csv", index=False)


def main():
    url = "https://www.instacart.ca/store/s?k=grocaries&search_source=logged_out_home_cross_retailer_search&search_id=dcad0c19-d1b2-4ef0-8f42-6634cc969cd6&page_view_id=52d1fe9a-7c42-5cb8-b33a-cbd4845b22a2"
    
    # Initialize the driver
    driver = initialize_driver(url)
    
    # Hold all scraped products
    all_products = []
    
    # Click the 'Next page' button up to 10 times, or until it no longer appears
    max_clicks = 100
    for _ in range(max_clicks):
        time.sleep(5)  # Give time for the page to load fully after each click
        
        # Scrape the current page's products
        html = driver.page_source
        products = scrape_instacart_data(html)
        all_products.extend(products)
        
        # Try to click the 'Next page' button
        if not click_next_page_button(driver):
            print("No more 'Next page' button found, stopping.")
            break
    
    # Quit the driver after scraping
    driver.quit()
    
    # Create a DataFrame and write to a CSV
    if all_products:
        product_df = pd.DataFrame(all_products)
        write_csv(product_df, "instacart_products")
        print("Web Scraping and CSV file writing complete!")
    else:
        print("No products were scraped.")


if __name__ == "__main__":
    main()
