import scrapy
import json
import os


class AvFirstRunSpider(scrapy.Spider):
    name = "av_first_run"
    custom_settings = {
        "ITEM_PIPELINES": {
            "fanza.pipelines.AVPipeline": 300,
        }
    }

    async def start(self):
        query_path = os.path.join(os.path.dirname(
            __file__), '..', 'query', 'av_search.graphql')
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        makers = []
        url = "https://api.video.dmm.co.jp/graphql"
        for maker in makers:
            payload = {
                "query": query,
                "variables": {
                    "filter": {
                        "isSaleItemsOnly": False,
                        "makerIds": {
                            "ids": [
                                {
                                    "id": maker
                                }
                            ],
                            "op": "AND"
                        }
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
        for content in result["contents"]:
            item_payload = {
                "query": item_query,
                "variables": {
                    "id": content["id"],
                    "isAmateur": False,
                    "isAnime": False,
                    "isAv": True
                }
            }
            yield scrapy.Request(
                url=response.url,
                method="POST",
                body=json.dumps(item_payload),
                callback=self.parse_item,
                meta={"maker_id": response.meta["payload"]["variables"]["filter"]["makerIds"]["ids"][0]["id"]}
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
        item["maker_id"] = response.meta["maker_id"]
        yield item
