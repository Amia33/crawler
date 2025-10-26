import scrapy
import json
import os


class ActressSpider(scrapy.Spider):
    name = "actress"
    custom_settings = {
        "ITEM_PIPELINES": {
            "fanza.pipelines.ActressPipeline": 300,
        }
    }

    async def start(self):
        query_path = os.path.join(os.path.dirname(
            __file__), '..', 'query', 'actress_syllabary.graphql')
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        url = "https://api.video.dmm.co.jp/graphql"
        payload = {
            "query": query,
            "variables": {
                "limit": 500,
                "offset": 0
            }
        }
        yield scrapy.Request(
            url=url,
            method="POST",
            body=json.dumps(payload),
            callback=self.parse,
            meta={"payload": payload}
        )

    def parse(self, response):
        data = json.loads(response.text)
        item = data["data"]["actresses"]
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
