from bs4 import BeautifulSoup
import requests
import csv


walmart_prefix = "https://www.walmart.com"


def scrape_products(page_number, writer):
    URL = f"https://www.walmart.com/search?query=laptop&page={page_number}&affinityOverride=store_led"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    pagination_list_div = soup.find_all("li", class_="flex flex-column items-center")
    print("Pagination", pagination_list_div)

    # Scrape product data
    product_result_div = soup.find("div", {"data-testid": "item-stack"})
    if product_result_div:
        products = product_result_div.find_all("div", {"role": "group"})

        for product in products:
            title_tag = product.find("span", {"data-automation-id": "product-title"})
            title = title_tag.text if title_tag else "No title available"

            link_element = product.find(
                "a", class_="w-100 h-100 z-1 hide-sibling-opacity absolute"
            )
            href_value = (
                link_element["href"]
                if link_element and link_element.get("href")
                else ""
            )

            # Ensure the link includes the Walmart prefix
            link = (
                (
                    href_value
                    if href_value.startswith(walmart_prefix)
                    else f"{walmart_prefix}{href_value}"
                )
                if href_value
                else ""
            )

            price_container = product.find(
                "div", {"data-automation-id": "product-price"}
            )

            # Extract the whole and fractional parts of the price
            if price_container:
                price_whole = (
                    price_container.find("span", class_="f2").text
                    if price_container.find("span", class_="f2")
                    else "0"
                )

                # Find the span with a specific style (vertical-align: 0.75ex)
                price_fraction_tag = price_container.find(
                    "span", style="vertical-align:0.75ex"
                )
                price_fraction = price_fraction_tag.text if price_fraction_tag else "00"

                price = f"${price_whole}.{price_fraction}"
            else:
                price = "Price not found"

            rating_tag = product.find("span", {"data-testid": "product-ratings"})
            product_rating = (
                rating_tag["data-value"]
                if rating_tag and rating_tag.get("data-value")
                else "No rating"
            )

            reviewer_count = product.find("span", {"data-testid": "product-reviews"})
            reviewer_count = (
                reviewer_count["data-value"]
                if reviewer_count and reviewer_count.get("data-value")
                else "No reviews"
            )

            # Write the extracted data to the CSV
            writer.writerow([title, link, price, product_rating, reviewer_count])
            print(f"Title: {title}")
            print(f"Link: {link}")
            print(f"Price: {price}")
            print(f"Product Rating: {product_rating}")
            print(f"Reviewer Count: {reviewer_count}\n")


with open("walmart_groceries.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(["Title", "Link", "Price", "Product Rating", "Reviewer Count"])

    for page in range(1, 11):
        print(f"Scraping page {page}...\n")
        scrape_products(page, writer)

print("Data has been successfully written to walmart_groceries.csv.")
