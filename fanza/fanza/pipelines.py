import pymongo
from itemadapter import ItemAdapter
import os
from scrapy.exceptions import NotConfigured


class MongoPipeline:

    def __init__(self, mongo_uri, mongo_db, crawler):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        mongo_uri = os.environ.get(
            'MONGO_URI') or crawler.settings.get('MONGO_URI')
        if not mongo_uri:
            raise NotConfigured(
                'MONGO_URI is not set in the environment or settings file.')
        return cls(
            mongo_uri=mongo_uri,
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'fanza'),
            crawler=crawler
        )

    def open_spider(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider = self.crawler.spider  # Get spider from the crawler
        self.db[spider.target].create_index('id', unique=True)
        if spider.target == 'av':
            self.db['histrion'].create_index('id', unique=True)
            self.db['director'].create_index('id', unique=True)

    def close_spider(self):
        self.client.close()

    def process_item(self, item):
        spider = self.crawler.spider  # Get spider from the crawler
        collection_name = item['collection']
        data_to_insert = item['data']
        collection = self.db[collection_name]
        try:
            collection.insert_one(data_to_insert)
            spider.logger.info(
                f"Inserted item with id '{data_to_insert.get('id')}' into '{collection_name}'")
        except pymongo.errors.DuplicateKeyError:
            spider.logger.warning(
                f"Item with id '{data_to_insert.get('id')}' already exists in '{collection_name}'")
        if collection_name == 'av':
            self.process_related(data_to_insert, spider,
                                 'histrions', 'histrion')
            self.process_related(data_to_insert, spider,
                                 'directors', 'director')
        return item

    def process_related(self, item_data, spider, item_key, collection_name):
        related_items = item_data.get(item_key, [])
        if not related_items:
            return
        collection = self.db[collection_name]
        for related_item in related_items:
            try:
                collection.insert_one(related_item)
                spider.logger.info(
                    f"Inserted related item with id '{related_item.get('id')}' into '{collection_name}'")
            except pymongo.errors.DuplicateKeyError:
                spider.logger.warning(
                    f"Related item with id '{related_item.get('id')}' already exists in '{collection_name}'")
