from pymongo.mongo_client import MongoClient
from dateutil import parser


class AnimePipeline:
    def open_spider(self, spider):
        self.mongo_cli = MongoClient()
        self.mongo_db = self.mongo_cli["fanza"]
        self.mongo_colle = self.mongo_db["anime"]

    def process_item(self, item, spider):
        fixed = {
            "_id": item["id"],
            "title": item["title"],
            "date": parser.isoparse(item["deliveryStartDate"]),
            "duration": item["duration"],
            "maker": int(item["maker"]["id"]),
            "exclusive": item["isExclusiveDelivery"],
            "description": item["description"],
            "notice": "",
            "full_id": None,
            "label": None,
            "series": None,
            "genre": [],
            "cover": {
                "large": None,
                "medium": item["packageImage"]["mediumUrl"]
            },
            "sample": {
                "image": {
                    "count": 0,
                    "url": []
                },
                "video": None
            }
        }
        if item["notices"]:
            for notice in item["notices"]:
                fixed["notice"] += (notice + "\n")
        if item["packageImage"]["largeUrl"]:
            fixed["cover"]["large"] = item["packageImage"]["largeUrl"]
        if item["sampleImages"]:
            fixed["sample"]["image"]["count"] = item["sampleImages"][-1]["number"]
            for image in item["sampleImages"]:
                if image["largeImageUrl"]:
                    fixed["sample"]["image"]["url"].append(
                        image["largeImageUrl"])
                else:
                    fixed["sample"]["image"]["url"].append(image["imageUrl"])
        if item["sample2DMovie"]:
            fixed["sample"]["video"] = item["sample2DMovie"]["highestMovieUrl"]
        if item["series"]:
            fixed["series"] = int(item["series"]["id"])
        if item["label"]:
            fixed["label"] = int(item["label"]["id"])
        if item["genres"]:
            for genre in item["genres"]:
                fixed["genre"].append(int(genre["id"]))
        if "makerContentId" in item:
            fixed["full_id"] = item["makerContentId"]
        if self.mongo_colle.find_one({"_id": fixed["_id"]}):
            spider.logger.info(
                f"Skipped duplicate item with _id={fixed["_id"]}")
        else:
            self.mongo_colle.insert_one(fixed)

    def close_spider(self, spider):
        self.mongo_cli.close()


class GenrePipeline:
    def open_spider(self, spider):
        self.mongo_cli = MongoClient()
        self.mongo_db = self.mongo_cli["fanza"]
        self.mongo_colle = self.mongo_db["genre"]

    def process_item(self, item, spider):
        for genre in item["items"]:
            fixed = {
                "_id": int(genre["id"]),
                "name": genre["name"]
            }
            if self.mongo_colle.find_one({"_id": fixed["_id"]}):
                spider.logger.info(
                    f"Skipped duplicate item with _id={fixed["_id"]}")
            else:
                self.mongo_colle.insert_one(fixed)

    def close_spider(self, spider):
        self.mongo_cli.close()


class MakerPipeline:
    def open_spider(self, spider):
        self.mongo_cli = MongoClient()
        self.mongo_db = self.mongo_cli["fanza"]
        self.mongo_colle = self.mongo_db["maker"]

    def process_item(self, item, spider):
        for maker in item["items"]:
            fixed = {
                "_id": int(maker["id"]),
                "name": maker["name"],
                "image": None,
                "description": None,
                "exclusive": maker["isExclusive"]
            }
            if maker["imageUrl"]:
                fixed["image"] = maker["imageUrl"]
            if maker["description"]:
                fixed["description"] = maker["description"]
            if self.mongo_colle.find_one({"_id": fixed["_id"]}):
                spider.logger.info(
                    f"Skipped duplicate item with _id={fixed["_id"]}")
            else:
                self.mongo_colle.insert_one(fixed)

    def close_spider(self, spider):
        self.mongo_cli.close()


class SeriesPipeline:
    def open_spider(self, spider):
        self.mongo_cli = MongoClient()
        self.mongo_db = self.mongo_cli["fanza"]
        self.mongo_colle = self.mongo_db["series"]

    def process_item(self, item, spider):
        for series in item["items"]:
            fixed = {
                "_id": int(series["id"]),
                "name": series["name"],
                "description": series["description"]
            }
            if self.mongo_colle.find_one({"_id": fixed["_id"]}):
                spider.logger.info(
                    f"Skipped duplicate item with _id={fixed["_id"]}")
            else:
                self.mongo_colle.insert_one(fixed)

    def close_spider(self, spider):
        self.mongo_cli.close()


class LabelPipeline:
    def open_spider(self, spider):
        self.mongo_cli = MongoClient()
        self.mongo_db = self.mongo_cli["fanza"]
        self.mongo_colle = self.mongo_db["label"]

    def process_item(self, item, spider):
        for label in item["items"]:
            fixed = {
                "_id": int(label["id"]),
                "name": label["name"],
                "image": None,
                "description": None
            }
            if label["imageUrl"]:
                fixed["image"] = label["imageUrl"]
            if label["description"]:
                fixed["description"] = label["description"]
            if self.mongo_colle.find_one({"_id": fixed["_id"]}):
                spider.logger.info(
                    f"Skipped duplicate item with _id={fixed["_id"]}")
            else:
                self.mongo_colle.insert_one(fixed)

    def close_spider(self, spider):
        self.mongo_cli.close()


class ActressPipeline:
    def open_spider(self, spider):
        self.mongo_cli = MongoClient()
        self.mongo_db = self.mongo_cli["fanza"]
        self.mongo_colle = self.mongo_db["actress"]

    def process_item(self, item, spider):
        for actress in item["items"]:
            fixed = {
                "_id": int(actress["id"]),
                "name": actress["name"],
                "nickname": actress["nameRuby"],
                "image": actress["imageUrl"],
                "count": actress["contentsCount"]
            }
            if self.mongo_colle.find_one({"_id": fixed["_id"]}):
                spider.logger.info(
                    f"Skipped duplicate item with _id={fixed["_id"]}")
            else:
                self.mongo_colle.insert_one(fixed)

    def close_spider(self, spider):
        self.mongo_cli.close()


class AmateurPipeline:
    def open_spider(self, spider):
        self.mongo_cli = MongoClient()
        self.mongo_db = self.mongo_cli["fanza"]
        self.mongo_colle = self.mongo_db["amateur"]

    def process_item(self, item, spider):
        fixed = {
            "_id": item["id"],
            "title": item["title"],
            "date": parser.isoparse(item["deliveryStartDate"]),
            "duration": item["duration"],
            "maker": int(item["maker"]["id"]),
            "label": int(item["label"]["id"]),
            "exclusive": item["isExclusiveDelivery"],
            "description": item["description"],
            "notice": "",
            "full_id": None,
            "genre": [],
            "cover": item["packageImage"]["mediumUrl"],
            "sample": {
                "image": {
                    "count": 0,
                    "url": []
                },
                "video": None
            },
            "actress": {
                "name": item["amateurActress"]["name"],
                "age": None,
                "waist": None,
                "bust": None,
                "cup": None,
                "height": None,
                "hip": None
            }
        }
        if item["notices"]:
            for notice in item["notices"]:
                fixed["notice"] += (notice + "\n")
        if item["sampleImages"]:
            fixed["sample"]["image"]["count"] = item["sampleImages"][-1]["number"]
            for image in item["sampleImages"]:
                if image["largeImageUrl"]:
                    fixed["sample"]["image"]["url"].append(
                        image["largeImageUrl"])
                else:
                    fixed["sample"]["image"]["url"].append(image["imageUrl"])
        if item["sample2DMovie"]:
            fixed["sample"]["video"] = item["sample2DMovie"]["highestMovieUrl"]
        if item["genres"]:
            for genre in item["genres"]:
                fixed["genre"].append(int(genre["id"]))
        if "makerContentId" in item:
            fixed["full_id"] = item["makerContentId"]
        if item["amateurActress"]["age"]:
            fixed["actress"]["age"] = item["amateurActress"]["age"]
        if item["amateurActress"]["waist"]:
            fixed["actress"]["waist"] = item["amateurActress"]["waist"]
        if item["amateurActress"]["bust"]:
            fixed["actress"]["bust"] = item["amateurActress"]["bust"]
        if item["amateurActress"]["bustCup"]:
            fixed["actress"]["cup"] = item["amateurActress"]["bustCup"]
        if item["amateurActress"]["height"]:
            fixed["actress"]["height"] = item["amateurActress"]["height"]
        if item["amateurActress"]["hip"]:
            fixed["actress"]["hip"] = item["amateurActress"]["hip"]
        if self.mongo_colle.find_one({"_id": fixed["_id"]}):
            spider.logger.info(
                f"Skipped duplicate item with _id={fixed["_id"]}")
        else:
            self.mongo_colle.insert_one(fixed)

    def close_spider(self, spider):
        self.mongo_cli.close()
