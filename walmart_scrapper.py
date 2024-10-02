from bs4 import BeautifulSoup
import requests


URL = "https://www.walmart.com/search/?query=groceries"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}


page = requests.get(URL, headers=headers)


soup = BeautifulSoup(page.content, "html.parser")


products = soup.find_all("div", {"role": "group"})


for product in products:
    title_tag = product.find("span", {"data-automation-id": "product-title"})
    title = title_tag.text if title_tag else "No title available"
    link = product.find("a", class_="w-100 h-100 z-1 hide-sibling-opacity  absolute")
    link = (
        "https://www.walmart.com" + product.a["href"]
        if product.a and product.a.get("href")
        else "No link available"
    )

    price_container = product.find("div", {"data-automation-id": "product-price"})

    # Extract the whole and fractional parts of the price
    if price_container:
        price_whole = (
            price_container.find("span", class_="f2").text
            if price_container.find("span", class_="f2")
            else "0"
        )

        # Find the span with a specific style (vertical-align: 0.75ex)
        price_fraction_tag = price_container.find("span", style="vertical-align:0.75ex")
        price_fraction = price_fraction_tag.text if price_fraction_tag else "00"

        price = f"${price_whole}.{price_fraction}"
    else:
        price = "Price not available"

    # Print the extracted data
    print(f"Title: {title}")
    print(f"Link: {link}")
    print(f"Price:{price}")
