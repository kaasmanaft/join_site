import requests
import time
import concurrent.futures
import threading
from django.db import connection
thread_local = threading.local()


def get_session():
    if not hasattr(thread_local,'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def download_site(url):
    session = get_session()
    with session.get(url) as response:
        print(f"Read {len(response.content)}  from {url} session  {id(session)}")

def download_all_sites(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(download_site, sites)

# items 0.0
# category 0.0
# get page 0.0
# number_items_on_page 0.0
# paginator 0.0
# items_page 2.5441455841064453
# cards 4.2452428340911865
# context 0.0
# loader 12.164695739746094
# list_view -> 18.962084770202637 sec
# [06/Sep/2019 00:59:18] "GET /product/category/top/ HTTP/1.1" 200 56684
{'sql': 'SELECT "product_item"."id", "product_item"."agg_photos", "product_item"."base_photo_url", "product_item"."name" FROM "product_item" WHERE (NOT ("product_item"."
agg_photos" IS NULL) AND UPPER("product_item"."name"::text) LIKE UPPER(\'%платок%\')) ORDER BY "product_item"."id" ASC  LIMIT 24', 'time': '0.066'}
{'sql': 'SELECT "product_item"."id", "product_item"."agg_photos", "product_item"."base_photo_url", "product_item"."name" FROM "product_item" WHERE (NOT ("product_item"."
agg_photos" IS NULL) AND UPPER("product_item"."name"::text) LIKE UPPER(\'%платок%\')) ORDER BY "product_item"."name" ASC  LIMIT 24', 'time': '11.132'}


if __name__ == "__main__":
    sites = [
        "https://www.jython.org",
        "http://olympus.realpython.org/dice",
    ] * 80
    start_time = time.time()
    download_all_sites(sites)
    duration = time.time() - start_time

    print(f"Downloaded {len(sites)} in {duration} seconds")