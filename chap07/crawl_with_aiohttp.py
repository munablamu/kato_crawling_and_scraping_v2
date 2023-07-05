import asyncio
import logging

import aiohttp
import feedparser
from bs4 import BeautifulSoup


async def main():
    """
    メインとなる処理のコルーチン。はてなブックマークの人気エントリーを非同期でクロールする。
    """
    d = feedparser.parse('http://b.hatena.ne.jp/hotentry.rss')
    urls = [entry.link for entry in d.entries]
    # 同時リクエスト数を全体で5に、ホスト単位で1に制限するTCPConnectorオブジェクトを作成。
    connector = aiohttp.TCPConnector(limit=5, limit_per_host=1) 
    # セッションオブジェクトを作成。
    async with aiohttp.ClientSession(connector=connector) as session:
        # URLのリストに対応するコルーチンのリストを作成。
        coroutines = []
        for url in urls:
            coroutine = fetch_and_scrape(session, url)
            coroutines.append(coroutine)

        # コルーチンを並行実行し、完了した順に返す。
        for coroutine in asyncio.as_completed(coroutines):
            print(await coroutine)


async def fetch_and_scrape(session: aiohttp.ClientSession, url: str) -> dict:
    """
    引数で指定したURLのページを取得して、URLとタイトルを含むdictを返すコルーチン。

    Args:
        session (aiohttp.ClientSession): _description_
        url (str): _description_

    Returns:
        dict: _description_
    """
    logging.info(f'Request queued {url}')
    # 非同期にリクエストを送り、レスポンスヘッダを取得する。
    async with session.get(url) as response:
        # レスポンスボディを非同期に取得してパースする。
        soup = BeautifulSoup(await response.read(), 'lxml')
        return {
            'url': url,
            'title': soup.title.text.strip(),
        }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
