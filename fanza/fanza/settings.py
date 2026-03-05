BOT_NAME = "fanza"
SPIDER_MODULES = ["fanza.spiders"]
NEWSPIDER_MODULE = "fanza.spiders"
USER_AGENT = "Amia33/crawler (https://github.com/Amia33/crawler)"
DOWNLOAD_DELAY = 0.25
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
LOG_LEVEL = 'WARNING'
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
}
ITEM_PIPELINES = {
    "fanza.pipelines.MongoPipeline": 300,
}
MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DATABASE = "fanza"
