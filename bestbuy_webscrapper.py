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
    assert "Best Buy Canada | Best Buy Canada" in driver.title
    return driver


def click_show_more_button(driver):
    """Click the 'Show more' button to load additional products."""
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Show more']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(2)  # Allow UI to settle
        driver.execute_script("arguments[0].click();", button)
        print('"Show more" button has been clicked via JavaScript')
        return True
    except Exception as e:
        print(f"Failed to click the button: {e}")
        return False


def scrape_laptop_data(html):
    """Extract laptop data from the HTML content."""
    html_soup = BeautifulSoup(html, "html.parser")
    laptop_containers = html_soup.find_all(
        "div",
        class_="style-module_col-xs-12__TFIB5 style-module_col-sm-4__DDhS- style-module_col-lg-3__bENCh x-productListItem productLine_2N9kG",
    )

    products = []
    for laptop in laptop_containers:
        product_info = {
            "Name": extract_product_name(laptop),
            "Price": extract_product_price(laptop),
            "Rating": extract_product_rating(laptop),
            "Number of Reviews": extract_reviewer_count(laptop),
            "Product Link": extract_product_link(laptop),
        }
        products.append(product_info)
    return products


def extract_product_name(laptop):
    """Extract the product name."""
    name_tag = laptop.find("div", class_="productItemName_3IZ3c")
    if not name_tag:
        name_tag = laptop.select_one("div[data-automation='product-title']")
    return name_tag.text.strip() if name_tag else "N/A"


def extract_product_price(laptop):
    """Extract the product price."""
    price_container = laptop.find("span", attrs={"data-automation": "product-price"})
    return price_container.find("div").text.strip() if price_container else "N/A"


def extract_product_rating(laptop):
    """Extract the product rating."""
    rating_meta = laptop.find("meta", attrs={"itemprop": "ratingValue"})
    return float(rating_meta["content"]) if rating_meta else None


def extract_reviewer_count(laptop):
    """Extract the number of reviews."""
    review_count_span = laptop.find("span", attrs={"data-automation": "rating-count"})
    if review_count_span:
        review_count = review_count_span.text.strip()[1:-1]
        return int(review_count.split()[0])
    return 0


def extract_product_link(laptop):
    """Extract the product link."""
    link_tag = laptop.find("a", href=True)
    return f"https://www.bestbuy.ca{link_tag['href']}" if link_tag else "N/A"


def write_csv(dataframe, file_name):
    """Write the DataFrame to a CSV file."""
    dataframe.to_csv(f"{file_name}.csv", index=False)


def main():
    url = "https://www.bestbuy.ca/en-ca/search?search=laptop"
    driver = initialize_driver(url)

    # Click the 'Show more' button multiple times
    max_clicks = 5
    for _ in range(max_clicks):
        time.sleep(3)
        if not click_show_more_button(driver):
            break

    html = driver.page_source
    driver.quit()
    print("Driver has been quit")

    products = scrape_laptop_data(html)

    # Create DataFrame and write to CSV
    laptop_dataframe = pd.DataFrame(products)
    write_csv(laptop_dataframe, "bestbuy")
    print("Web Scraping and CSV file writing complete!")


if __name__ == "__main__":
    main()
