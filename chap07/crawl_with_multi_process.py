import concurrent.futures
import logging

import feedparser
import requests
from bs4 import BeautifulSoup


def main():
    d = feedparser.parse('http://b.hatena.ne.jp/hotentry.rss')
    urls = [entry.link for entry in d.entries]
    logging.info(f'Extracted {len(urls)} URLs')

    # 最大3プロセスで並行処理するためのExecutorオブジェクトを作成。
    executer = concurrent.futures.ProcessPoolExecutor(max_workers=3)
    futures = []    # Futureオブジェクトを格納しておくためのリスト
    for url in urls:
        # 関数の実行スケジューリングし、Futureオブジェクトを得る。
        future = executer.submit(fetch_and_scrape, url)
        futures.append(future)

    # Futureオブジェクトを完了したものから取得する。
    for future in concurrent.futures.as_completed(futures):
        print(future.result()) # Futureオブジェクトから結果(関数の戻り値)を取得して表示する。


def fetch_and_scrape(url: str) -> dict:
    """
    引数で指定したURLのページを取得して、URLとタイトルを含むdictを返す。

    Args:
        url (str): _description_

    Returns:
        dict: _description_
    """
    logging.info(f'Start downloading {url}')

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    return {
        'url': url,
        'title': soup.title.text.strip(),
    }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(process)d] %(message)s')
    main()
