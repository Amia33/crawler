import scrapy


class AnimeSpider(scrapy.Spider):
    name = "anime"
    allowed_domains = ["dmm.co.jp"]
    start_urls = ["https://dmm.co.jp"]

    def parse(self, response):
        pass
