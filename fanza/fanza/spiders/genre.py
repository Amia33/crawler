import scrapy
import json
import os


class GenreSpider(scrapy.Spider):
    name = "genre"
    custom_settings = {
        "ITEM_PIPELINES": {
            "fanza.pipelines.GenrePipeline": 300,
        }
    }

    async def start(self):
        query_path = os.path.join(os.path.dirname(
            __file__), '..', 'query', 'genre_list_syllabary.graphql')
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        url = "https://api.video.dmm.co.jp/graphql"
        floors = ["ANIME", "AMATEUR", "AV"]
        payload = {
            "query": query,
            "variables": {
                "floor": ""
            }
        }
        for floor in floors:
            payload["variables"]["floor"] = floor
            yield scrapy.Request(
                url=url,
                method="POST",
                body=json.dumps(payload),
                callback=self.parse
            )

    def parse(self, response):
        data = json.loads(response.text)
        item = data["data"]["genres"]
        yield item
