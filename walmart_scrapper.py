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

    # Print the extracted data
    print(f"Title: {title}")
    print(f"Link: {link}")
