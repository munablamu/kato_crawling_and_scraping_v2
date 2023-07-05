import time
import re
from typing import Iterator
import logging

import requests
import lxml.html
from pymongo import MongoClient

from scraper_tasks import scrape


def main():
    """
    クローラーのメイン処理。
    """
    client = MongoClient('localhost', 27017)
    collection = client.scraping.ebook_htmls
    collection.create_index('key', unique=True)

    session = requests.Session()
    response = session.get('https://gihyo.jp/dp')
    urls = scrape_list_page(response)
    for url in urls:
        key = extract_key(url)

        ebook_html = collection.find_one({'key': key})
        if not ebook_html:
            time.sleep(1)
            logging.info(f'Fetching {url}')
            response = session.get(url)

            collection.insert_one({
                'url': url,
                'key': key,
                'html': response.content,
            })
            scrape.delay(key)


def scrape_list_page(response: requests.Response) -> Iterator[str]:
    """
    一覧ページのResponseから詳細ページのURLを抜き出すジェネレーター関数.

    Args:
        response (requests.Response): _description_

    Yields:
        Iterator[str]: _description_
    """
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(response.url)

    for a in html.cssselect('#listBook > li > a[itemprop="url"]'):
        url = a.get('href')
        yield url


def extract_key(url: str) -> str:
    """
    URLからキー(urlの末尾のISBN)を抜き出す.

    Args:
        url (url): _description_

    Returns:
        str: _description_
    """
    m = re.search(r'/([^/]+)$', url)
    return m.group(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
