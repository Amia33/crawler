#!/bin/bash
export MONGO_URI="mongodb://127.0.0.1:27017"
CRAWLERS=("refresh" "genre" "maker" "series" "label" "actress")
for CRAWLER in "${CRAWLERS[@]}"
do
  echo "Running crawler: $CRAWLER"
  scrapy crawl graphql -a target="$CRAWLER"
  echo "Finished crawler: $CRAWLER"
done
echo "All crawlers have been run."
