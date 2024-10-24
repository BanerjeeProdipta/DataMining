import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup

class AmazonSpider(scrapy.Spider):
    name = "amazon_spider"

    def start_requests(self):
        base_url = "https://www.amazon.ca/s?k=laptop&crid=1E63C3THFEGDP&sprefix=laptop%2Caps%2C128&ref=nb_sb_noss_1"
        for i in range(1, 151):
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
            "Product Title": title,
            "Product Link": link,
            "Product Price": price,
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

        

        # Extract 'Frequently Bought Together' items
        fbt_sections = soup.find_all("div", class_="a-section a-spacing-none a-spacing-top-base _p13n-desktop-sims-fbt_fbt-desktop_plus-padding__21zgg")
        frequently_bought = []
        print("fbt_sections",fbt_sections)

        # Assuming fbt_sections contains the correctly found elements from the soup
        for fbt_item in fbt_sections:
            # Find the link and title
            fbt_link_tag = fbt_item.find("a", class_="a-link-normal")
            
            if fbt_link_tag:
                # Construct the product link
                fbt_link = "https://www.amazon.ca" + fbt_link_tag["href"]
                
                # Extract the product title from the <span> inside the link
                fbt_product_title = fbt_link_tag.find("span", class_="a-size-base").get_text(strip=True)

                # Extract the price from the price section
                price_tag = fbt_item.find("span", class_="a-offscreen")
                price = price_tag.get_text(strip=True) if price_tag else "Price not available"

                frequently_bought.append({"Title": fbt_product_title, "Link": fbt_link, "Price": price})

        product_data["Frequently Bought Together"] = ", ".join(frequently_bought) or "Not available"

       
        yield product_data


def run_spider():
    """Run the Scrapy spider and configure logging."""
    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
    runner = CrawlerRunner(
        settings={
            "FEEDS": {
                "amazon.csv": {
                    "format": "csv",
                    "encoding": "utf8",
                    "fields": [
                        "Product Title",
                        "Product Link",
                        "Product Price",
                        "Rating",
                        "Number of Reviews",
                        "Frequently Bought Together",
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
