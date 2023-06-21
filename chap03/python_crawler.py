import re
import time
from typing import Iterator
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pymongo import MongoClient


def main():
    """
    クローラーのメインの処理
    """
    client = MongoClient('localhost', 27017)
    collection = client.scraping.ebooks
    collection.create_index('key', unique=True)

    session = requests.Session()
    response = requests.get('https://gihyo.jp/dp')

    urls = scrape_list_page(response)
    for url in urls:
        key = extract_key(url) # URLからキーを取得する

        ebook = collection.find_one({'key': key})
        if not ebook:
            time.sleep(1)
            response = session.get(url)
            ebook = scrape_detail_page(response)
            collection.insert_one(ebook)

        print(ebook)


def scrape_list_page(response: requests.Response) -> Iterator[str]:
    """
    一覧ページのResponseから詳細ページのURLを抜き出すジェネレーター関数

    Args:
        response (requests.Response):

    Yields:
        Iterator[str]:
    """
    soup = BeautifulSoup(response.text, 'html.parser')

    for a in soup.select('#listBook > li > a[itemprop="url"]'):
        url = urljoin(response.url, a.get('href'))
        yield url


def scrape_detail_page(response: requests.Response) -> dict:
    """
    詳細ページのResponseから電子書籍の情報をdictで取得する

    Args:
        response (requests.Response):

    Returns:
        dict: 電子書籍データ
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    ebook = {
        'url'    : response.url, # URL
        'key'    : extract_key(response.url), # URLから抜き出したキー
        'title'  : soup.select_one('#bookTitle').text, # タイトル
        'price'  : soup.select_one('.buy').contents[0].strip(), # 価格
        'content': [normalize_spaces(h3.text) for h3 in soup.select('#content > h3')], # 目次
    }
    return ebook


def extract_key(url: str) -> str:
    """
    URLからキー(URLの末尾のISBN)を抜き出す

    Args:
        url (str): 対象URL

    Returns:
        str: キー(ISBN)
    """
    m = re.search(r'/([^/]+)$', url)
    return m.group(1)

def normalize_spaces(s: str) -> str:
    """
    連続する空白を1つのスペースに置き換え、前後の空白を削除した新しい文字列を取得する

    Args:
        s (str): 元の文字列

    Returns:
        str: 加工後の文字列
    """
    return re.sub(r'\s+', ' ', s).strip()

if __name__ == '__main__':
    main()
