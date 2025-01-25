import scrapy
from scrapy.crawler import CrawlerProcess

class WalmartSpider(scrapy.Spider):
    name = "walmart_spider"
    
    # List of search terms and number of pages to scrape
    search_terms = ["laptop", "smartphone", "headphones", "smartwatch", "camera", "speakers", "keyboard", "tablet", "tv", "mouse"]
    pages_to_scrape = 5

    def start_requests(self):
        base_url = "https://www.walmart.ca/en/browse/grocery/fruits-vegetables/fresh-vegetables/10019_6000194327370_6000194327412?icid=cp_l2_page_grocery_fresh_vegetables_shop_all_22969_MTSF26T9P4&facet=fulfillment_method%3ADelivery&page={page_number}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        for search_term in self.search_terms:
            for page_number in range(1, self.pages_to_scrape + 1):
                url = base_url.format(search_term=search_term, page_number=page_number)
                yield scrapy.Request(url=url, callback=self.parse_search_results, headers=headers)

    def parse_search_results(self, response):
        """Parse search result page to extract product details."""
        products = response.xpath("//div[@data-testid='item-stack']//div[@role='group']")
        
        for product in products:
            name = product.xpath(".//span[@data-automation-id='product-title']/text()").get(default="No name available").strip()
            link = product.xpath(".//a[@class='w-100 h-100 z-1 hide-sibling-opacity absolute']/@href").get(default="")
            price_whole = product.xpath(".//span[contains(@class, 'f2')]/text()").get(default="0")
            price_fraction = product.xpath(".//span[@style='vertical-align:0.75ex']/text()").get(default="00")
            
            price = f"${price_whole}.{price_fraction}" if price_whole != "0" else "Price not available"
            full_link = f"https://www.walmart.com{link}" if link.startswith("/") else link
            
            yield {
                "Name": name,
                "Price": price,
                "Product Link": full_link,
            }

# Configure and run the Scrapy spider
process = CrawlerProcess(settings={
    "FEEDS": {
        "walmart_products.json": {"format": "json", "encoding": "utf8", "indent": 4},
    },
    "USER_AGENT": "Mozilla/5.0",
    "LOG_LEVEL": "INFO",
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",  # Updated to avoid deprecation warning
})

process.crawl(WalmartSpider)
process.start()
