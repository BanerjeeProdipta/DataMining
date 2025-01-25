import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup

search_terms = ["laptop", "smartphone", "headphones", "smartwatch", "camera", "speakers", "keyboard", "tablet", "tv", "mouse"]

class AmazonSpider(scrapy.Spider):
    name = "amazon_spider"

    def start_requests(self):

        for search_term in search_terms:
            base_url = f"https://www.amazon.ca/s?k={search_term}&crid=1E63C3THFEGDP&sprefix={search_term}%2Caps%2C128&ref=nb_sb_noss_1"
            
            # Scrape multiple pages for each search term (adjust range as needed)
            for i in range(1, 5):  
                url = f"{base_url}&page={i}"
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_search_results,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
        base_url = "https://www.amazon.ca/s?k=electronics&crid=1E63C3THFEGDP&sprefix=electronics%2Caps%2C128&ref=nb_sb_noss_1"
        for i in range(1, 200):
            url = f"{base_url}&page={i}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_search_results,
                headers={"User-Agent": "Mozilla/5.0"},
            )

    def parse_search_results(self, response):
        """Parse the search results to get individual product links."""
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", class_="s-result-item")

        for product in products:
            product_data = self.extract_product_data(product)
            product_link = product_data.get("Product Link")
            if product_link != "No link available":
                yield scrapy.Request(
                    url=product_link,
                    callback=self.parse_product_detail,
                    meta={"product_data": product_data},
                    headers={"User-Agent": "Mozilla/5.0"},
                )

    def extract_product_data(self, product):
        """Extract basic product details."""
        title = self.extract_product_title(product)
        link = self.extract_product_link(product)
        price = self.extract_product_price(product)
        rating = self.extract_product_rating(product)
        num_reviews = self.extract_num_reviews(product)
        return {
            "Name": title,
            "Product Link": link,
            "Price": price,
            "Rating": rating,
            "Number of Reviews": num_reviews,
        }

    def extract_product_title(self, product):
        title_tag = product.find(
            "span", class_="a-size-base-plus a-color-base a-text-normal"
        )
        return title_tag.text.strip() if title_tag else "No title available"
    
    def extract_product_link(self, product):
        link = product.find("a", class_="a-link-normal")
        return "https://www.amazon.ca" + link["href"] if link else "No link available"

    def extract_product_price(self, product):
        price_whole = product.find("span", class_="a-price-whole")
        price_fraction = product.find("span", class_="a-price-fraction")
        return (
            price_whole.text + price_fraction.text
            if price_whole and price_fraction
            else "Price not available"
        )

    def extract_product_rating(self, product):
        rating_tag = product.find("span", {"aria-label": True})
        return (
            rating_tag["aria-label"].split(" out of ")[0]
            if rating_tag and rating_tag.get("aria-label")
            else "Rating not available"
        )

    def extract_num_reviews(self, product):
        reviews_tag = product.find("span", class_="a-size-base")
        return reviews_tag.text.strip() if reviews_tag else "No reviews available"

    def parse_product_detail(self, response):
        """Parse the product detail page for additional information."""
        product_data = response.meta["product_data"]
        soup = BeautifulSoup(response.text, "html.parser")
        print("Details: ", soup)

        # Just yield the basic product details
        yield product_data


def run_spider():
    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
    runner = CrawlerRunner(
        settings={
            "FEEDS": {
                "amazon.csv": {
                    "format": "csv",
                    "encoding": "utf8",
                    "fields": [
                        "Name",
                        "Price",
                        "Rating",
                        "Number of Reviews",
                        "Product Link"
                    ],
                },
            },
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        }
    )
    runner.crawl(AmazonSpider)
    reactor.run()


# Run the spider
if __name__ == "__main__":
    run_spider()
