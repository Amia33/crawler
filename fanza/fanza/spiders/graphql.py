import scrapy
import json
from pathlib import Path


class GraphqlSpider(scrapy.Spider):
    name = "graphql"
    allowed_domains = ["api.video.dmm.co.jp"]
    start_urls = ["https://api.video.dmm.co.jp/graphql"]
    graphql_dir = Path(__file__).parent.parent / 'graphql'

    def __init__(self, target=None, **kwargs):
        super().__init__(**kwargs)
        if target is None:
            raise ValueError("A 'target' argument must be provided.")
        self.target = target

    async def start(self):
        """Modern Scrapy entry point using async def."""
        self.load_queries()
        if self.target in ['anime', 'av', 'amateur']:
            yield from self.start_complex_target()
        else:
            yield from self.start_simple_target()

    # --- Helper Methods ---

    def load_queries(self):
        """Dynamically load GraphQL query files based on the target."""
        self.queries = {}
        required_files = {
            'anime': ['maker', 'anime_search', 'content'],
            'av': ['maker', 'av_search', 'content'],
            'amateur': ['label', 'amateur_search', 'content'],
        }.get(self.target, [self.target])

        for file_alias in required_files:
            try:
                with open(self.graphql_dir / f'{file_alias}.graphql', 'r') as f:
                    self.queries[file_alias] = f.read()
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"GraphQL query file not found: {self.graphql_dir / f'{file_alias}.graphql'}")

    def create_graphql_request(self, query_alias, variables, callback, meta=None):
        """Factory method for creating a GraphQL request."""
        return scrapy.Request(
            url=self.start_urls[0],
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps(
                {'query': self.queries[query_alias], 'variables': variables}),
            callback=callback,
            meta=meta or {}
        )

    # --- Unified Simple Target Logic ---

    def start_simple_target(self):
        target_floors = {
            'genre': ["AV", "AMATEUR", "ANIME"],
            'maker': ["AV", "AMATEUR", "ANIME"],
            'series': ["AV", "ANIME"],
            'label': ["AV", "AMATEUR", "ANIME"],
            'actress': ["AV"],
        }
        if self.target not in target_floors:
            raise ValueError(f"Invalid simple target: {self.target}")

        for floor in target_floors[self.target]:
            variables = {"floor": floor, "offset": 0}
            yield self.create_graphql_request(self.target, variables, self.parse_simple_items)

    def parse_simple_items(self, response):
        graphql_data = response.json().get('data', {}).get('graphql', {})
        items = graphql_data.get('items', [])

        for item in items:
            yield {
                'collection': self.target,
                'data': item
            }

        if graphql_data.get('pageInfo', {}).get('hasNext'):
            variables = json.loads(response.request.body)['variables']
            variables['offset'] += 500
            yield self.create_graphql_request(self.target, variables, self.parse_simple_items)

    # --- Complex Target Logic ---

    def start_complex_target(self):
        if self.target == 'anime':
            yield self.create_graphql_request('maker', {"floor": "ANIME", "offset": 0}, self.parse_makers)
        elif self.target == 'av':
            yield self.create_graphql_request('maker', {"floor": "AV", "offset": 0}, self.parse_makers)
        elif self.target == 'amateur':
            yield self.create_graphql_request('label', {"floor": "AMATEUR", "offset": 0}, self.parse_labels)

    def parse_makers(self, response):
        graphql_data = response.json().get('data', {}).get('graphql', {})
        for maker in graphql_data.get('items', []):
            search_variables = {
                "filter": {"makerIds": {"ids": [{"id": maker['id']}], "op": "AND"}},
                "offset": 0
            }
            search_alias = f'{self.target}_search'
            yield self.create_graphql_request(search_alias, search_variables, self.parse_content_search)

        if graphql_data.get('pageInfo', {}).get('hasNext'):
            variables = json.loads(response.request.body)['variables']
            variables['offset'] += 500
            yield self.create_graphql_request('maker', variables, self.parse_makers)

    def parse_labels(self, response):
        graphql_data = response.json().get('data', {}).get('graphql', {})
        for label in graphql_data.get('items', []):
            search_variables = {
                "filter": {"labelIds": {"ids": [{"id": label['id']}], "op": "AND"}},
                "offset": 0
            }
            yield self.create_graphql_request('amateur_search', search_variables, self.parse_content_search)

        if graphql_data.get('pageInfo', {}).get('hasNext'):
            variables = json.loads(response.request.body)['variables']
            variables['offset'] += 500
            yield self.create_graphql_request('label', variables, self.parse_labels)

    def parse_content_search(self, response):
        search_result = response.json().get(
            'data', {}).get('graphql', {}).get('result', {})
        for content in search_result.get('contents', []):
            content_variables = {
                "id": content['id'],
                "isAmateur": self.target == 'amateur',
                "isAnime": self.target == 'anime',
                "isAv": self.target == 'av'
            }
            yield self.create_graphql_request('content', content_variables, self.parse_content_details)

        if search_result.get('pageInfo', {}).get('hasNext'):
            variables = json.loads(response.request.body)['variables']
            variables['offset'] += 120
            search_alias = f'{self.target}_search'
            yield self.create_graphql_request(search_alias, variables, self.parse_content_search)

    def parse_content__details(self, response):
        content_data = response.json().get('data', {}).get('ppvContent')
        if content_data:
            yield {
                'collection': self.target,
                'data': content_data
            }
