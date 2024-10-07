import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup


class AmazonSpider(scrapy.Spider):
    name = "amazon_spider"

    def start_requests(self):
        """Generate requests for the first five pages of Amazon search results for laptops."""
        base_url = "https://www.amazon.ca/s?k=laptop&crid=1WXLR37VMDX3P&sprefix=laptop%2Caps%2C109&ref=nb_sb_noss_1"
        for i in range(1, 6):  # Scrape 5 pages of search results
            url = f"{base_url}&page={i}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={"User-Agent": "Mozilla/5.0"},
            )

    def parse(self, response):
        """Parse the response to extract product details."""
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", class_="s-result-item")

        for product in products:
            yield self.extract_product_data(product)

    def extract_product_data(self, product):
        """Extract and return product details as a dictionary."""
        title = self.extract_product_title(product)
        link = self.extract_product_link(product)
        price = self.extract_product_price(product)
        rating = self.extract_product_rating(product)
        num_reviews = self.extract_num_reviews(product)

        return {
            "Product Title": title,
            "Product Link": link,
            "Product Price": price,
            "Rating": rating,
            "Number of Reviews": num_reviews,
        }

    def extract_product_title(self, product):
        """Extract the product title."""
        title_tag = product.find(
            "span", class_="a-size-base-plus a-color-base a-text-normal"
        )
        return title_tag.text.strip() if title_tag else "No title available"

    def extract_product_link(self, product):
        """Extract the product link."""
        link = product.find("a", class_="a-link-normal")
        return "https://www.amazon.ca" + link["href"] if link else "No link available"

    def extract_product_price(self, product):
        """Extract the product price."""
        price_whole = product.find("span", class_="a-price-whole")
        price_fraction = product.find("span", class_="a-price-fraction")
        return (
            price_whole.text + price_fraction.text
            if price_whole and price_fraction
            else "Price not available"
        )

    def extract_product_rating(self, product):
        """Extract the product rating."""
        rating_tag = product.find("span", {"aria-label": True})
        return (
            rating_tag["aria-label"].split(" out of ")[0]
            if rating_tag and rating_tag.get("aria-label")
            else "Rating not available"
        )

    def extract_num_reviews(self, product):
        """Extract the number of reviews for the product."""
        reviews_tag = product.find("span", class_="a-size-base")
        return reviews_tag.text.strip() if reviews_tag else "No reviews available"


def run_spider():
    """Run the Scrapy spider and configure logging."""
    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
    runner = CrawlerRunner(
        settings={
            "FEEDS": {
                "amazon.csv": {
                    "format": "csv",  # Output to CSV
                    "encoding": "utf8",
                    "fields": [
                        "Product Title",
                        "Product Link",
                        "Product Price",
                        "Rating",
                        "Number of Reviews",
                    ],  # Fields to include in the CSV
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
