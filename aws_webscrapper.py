import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup


class AmazonSpider(scrapy.Spider):
    name = "amazon_spider"

    def start_requests(self):
        base_url = "https://www.amazon.ca/s?k=laptop&crid=1WXLR37VMDX3P&sprefix=laptop%2Caps%2C109&ref=nb_sb_noss_1"
        for i in range(1, 6):  # Scrape 5 pages of search results
            url = base_url + "&page=" + str(i)
            yield scrapy.Request(
                url=url, callback=self.parse, headers={"User-Agent": "Mozilla/5.0"}
            )

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", class_="s-result-item")

        for product in products:
            title = product.find(
                "span", class_="a-size-base-plus a-color-base a-text-normal"
            )
            title = title.text.strip() if title else "No title available"

            link = product.find("a", class_="a-link-normal")
            full_link = (
                "https://www.amazon.ca" + link["href"] if link else "No link available"
            )

            price_whole = product.find("span", class_="a-price-whole")
            price_fraction = product.find("span", class_="a-price-fraction")
            price = (
                price_whole.text + price_fraction.text
                if price_whole and price_fraction
                else "Price not available"
            )

            # Extract Rating
            rating_tag = product.find("span", {"aria-label": True})
            rating = (
                rating_tag["aria-label"].split(" out of ")[0]
                if rating_tag and rating_tag.get("aria-label")
                else "Rating not available"
            )

            # Extract Number of Reviews
            reviews_tag = product.find("span", class_="a-size-base")
            num_reviews = (
                reviews_tag.text.strip() if reviews_tag else "No reviews available"
            )

            yield {
                "Product Title": title,
                "Product Link": full_link,
                "Product Price": price,
                "Rating": rating,
                "Number of Reviews": num_reviews,
            }


def run_spider():
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
run_spider()
