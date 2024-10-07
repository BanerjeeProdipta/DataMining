import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def click_button(driver):
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Show more']]"))
        )

        # Scroll into view with a bit more scroll down
        driver.execute_script(
            "arguments[0].scrollIntoView(true); window.scrollBy(0, 100);", button
        )
        time.sleep(2)  # Adjust for any UI changes

        # Force click with JavaScript
        driver.execute_script("arguments[0].click();", button)
        print('"Show more" button has been clicked via JavaScript')
        return True

    except Exception as e:
        print(f"Failed to click the button: {e}")
        return False


def write_csv(dataframe, file_name):
    dataframe.to_csv(f"{file_name}.csv", index=False)


url = "https://www.bestbuy.ca/en-ca/search?search=laptop"

options = webdriver.ChromeOptions()
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)
driver.get(url)
driver.set_window_size(1200, 900)

print(driver.title)
assert "Best Buy Canada | Best Buy Canada" in driver.title

time.sleep(10)

max_clicks = 5
click_count = 0

while click_count < max_clicks:
    try:
        time.sleep(3)
        clicked = click_button(driver)

        if clicked:
            click_count += 1
        else:
            break

    except Exception as e:
        print("Button not found or click failed:", e)
        break

html = driver.page_source
driver.quit()
print("Driver has been quit")

html_soup = BeautifulSoup(html, "html.parser")
laptop_containers = html_soup.find_all(
    "div",
    class_="style-module_col-xs-12__TFIB5 style-module_col-sm-4__DDhS- style-module_col-lg-3__bENCh x-productListItem productLine_2N9kG",
)

names = []
prices = []
ratings = []
num_reviews = []
product_links = []

for laptop in laptop_containers:
    name_tag = laptop.find("div", class_="productItemName_3IZ3c")
    if not name_tag:
        name_tag = laptop.select_one("div[data-automation='product-title']")

    if name_tag:
        name = name_tag.text.strip()
        names.append(name)
    else:
        print("Product name not found")
        names.append("N/A")

    price_container = laptop.find("span", attrs={"data-automation": "product-price"})
    if price_container:
        price = price_container.find("div").text.strip()
        prices.append(price)
    else:
        prices.append("N/A")

    rating_meta = laptop.find("meta", attrs={"itemprop": "ratingValue"})
    if rating_meta:
        rating = float(rating_meta["content"])
        ratings.append(rating)
    else:
        ratings.append(None)

    review_count_span = laptop.find("span", attrs={"data-automation": "rating-count"})
    if review_count_span:
        review_count = review_count_span.text.strip()[1:-1]
        reviewer_count = int(review_count.split()[0])
        num_reviews.append(reviewer_count)
    else:
        num_reviews.append(0)

    link_tag = laptop.find("a", href=True)
    if link_tag:
        product_link = "https://www.bestbuy.ca" + link_tag["href"]
        product_links.append(product_link)
    else:
        product_links.append("N/A")

laptop_dict = {
    "Name": names,
    "Price": prices,
    "Rating": ratings,
    "Number of Reviews": num_reviews,
    "Product Link": product_links,
}

laptop_dataframe = pd.DataFrame(laptop_dict)

write_csv(laptop_dataframe, "bestbuy")
print("Web Scraping and CSV file writing complete!")
