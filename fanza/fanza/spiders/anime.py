import scrapy
import json
import os


class AnimeSpider(scrapy.Spider):
    name = "anime"
    custom_settings = {
        "ITEM_PIPELINES": {
            "fanza.pipelines.AnimePipeline": 300,
        }
    }

    async def start(self):
        query_path = os.path.join(os.path.dirname(
            __file__), '..', 'query', 'anime_search.graphql')
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        url = "https://api.video.dmm.co.jp/graphql"
        payload = {
            "query": query,
            "variables": {
                "filter": {
                    "isSaleItemsOnly": False
                },
                "limit": 120,
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
        result = data["data"]["legacySearchPPV"]["result"]
        item_query_path = os.path.join(os.path.dirname(
            __file__), '..', 'query', 'content_page_data.graphql')
        with open(item_query_path, "r", encoding="utf-8") as f:
            item_query = f.read()
        item_payload = {
            "query": item_query,
            "variables": {
                "id": "",
                "isAmateur": False,
                "isAnime": True,
                "isAv": False
            }
        }
        for content in result["contents"]:
            item_payload["variables"]["id"] = content["id"]
            yield scrapy.Request(
                url=response.url,
                method="POST",
                body=json.dumps(item_payload),
                callback=self.parse_item
            )
        if result["pageInfo"]["hasNext"]:
            next_payload = response.meta["payload"]
            next_payload["variables"]["offset"] += 120
            yield scrapy.Request(
                url=response.url,
                method="POST",
                body=json.dumps(next_payload),
                callback=self.parse,
                meta={"payload": next_payload}
            )

    def parse_item(self, response):
        data = json.loads(response.text)
        item = data["data"]["ppvContent"]
        yield item
