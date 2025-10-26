import scrapy
import json
import os


class SeriesSpider(scrapy.Spider):
    name = "series"
    custom_settings = {
        "ITEM_PIPELINES": {
            "fanza.pipelines.SeriesPipeline": 300,
        }
    }

    async def start(self):
        query_path = os.path.join(os.path.dirname(
            __file__), '..', 'query', 'series_list.graphql')
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        url = "https://api.video.dmm.co.jp/graphql"
        floors = ["ANIME", "AMATEUR", "AV"]
        payload = {
            "query": query,
            "variables": {
                "floor": "",
                "limit": 500,
                "offset": 0
            }
        }
        for floor in floors:
            payload["variables"]["floor"] = floor
            yield scrapy.Request(
                url=url,
                method="POST",
                body=json.dumps(payload),
                callback=self.parse,
                meta={"payload": payload}
            )

    def parse(self, response):
        data = json.loads(response.text)
        item = data["data"]["seriesList"]
        yield item
        if item["pageInfo"]["hasNext"]:
            next_payload = response.meta["payload"]
            next_payload["variables"]["offset"] += 500
            yield scrapy.Request(
                url=response.url,
                method="POST",
                body=json.dumps(next_payload),
                callback=self.parse,
                meta={"payload": next_payload}
            )
