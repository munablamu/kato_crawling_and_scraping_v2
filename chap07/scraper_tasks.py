import re

from pyqs import task
import lxml.html
from pymongo import MongoClient


@task(queue='ebook')
def scrape(key: str):
    """
    ワーカーで実行するタスク

    Args:
        key (str): _description_
    """
    client = MongoClient('localhost', 27017)
    html_collection = client.scraping.ebook_htmls

    ebook_html = html_collection.find_one({'key': key})
    ebook = scrape_detail_page(key, ebook_html['url'], ebook_html['html'])

    ebook_collection = client.scraping.ebooks
    ebook_collection.create_index('key', unique=True)
    ebook_collection.update_one({'key': key}, {'$set': ebook}, upsert=True)


def scrape_detail_page(key: str, url: str, html: str) -> dict:
    """
    詳細ページのResponseから電子書籍の情報をdictで得る。

    Args:
        key (str): _description_
        url (str): _description_
        html (str): _description_

    Returns:
        dict: _description_
    """
    root = lxml.html.fromstring(html)
    ebook = {
        'url': url,
        'key': key,
        'title': root.cssselect('#bookTitle')[0].text_content(),
        'price': root.cssselect('.buy')[0].text.strip(),
        'content': [normalize_spaces(h3.text_content()) for h3 in root.cssselect('#content > h3')],
    }
    return ebook


def normalize_spaces(s: str) -> str:
    """
    連続する空白を1つのスペースに置き換え、前後の空白を削除した新しい文字列を取得する。

    Args:
        s (str): _description_

    Returns:
        str: _description_
    """
    return re.sub(r'\s+', ' ', s).strip()
