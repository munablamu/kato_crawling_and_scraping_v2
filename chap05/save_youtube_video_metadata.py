import os
import logging
from typing import Iterator, List

from apiclient.discovery import build
from pymongo import MongoClient, ReplaceOne, DESCENDING
from pymongo.collection import Collection

YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


def main():
    """
    メインの処理。
    """
    mongo_client = MongoClient('localhost', 27017)
    collection = mongo_client.youtube.videos

    # 動画を検索し、ページ単位でアイテムのリストを保存する。
    for items_per_page in search_videos('手芸'):
        save_to_mongodb(collection, items_per_page)

    show_top_videos(collection)


def search_videos(query: str, max_pages: int=5) -> Iterator[List[dict]]:
    """
    引数queryで動画を検索して、ページ単位でアイテムのリストをyieldする。
    最大max_pagesページまで検索する。

    Args:
        query (str): _description_
        max_pages (int, optional): _description_. Defaults to 5.

    Yields:
        Iterator[List[dict]]: _description_
    """
    # YouTubeのAPIクライアントを組み立てる。
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # search.listメソッドで最初のページを取得するためのリクエストを得る。
    search_request = youtube.search().list(
        part='id', # search.listでは動画IDだけを取得できれば良い。
        q=query,
        type='video',
        maxResults=50, # 1ページあたり最大50件の動画を取得する。
    )

    # リクエストが有効、かつページ数がmax_pages以内の間、繰り返す。
    # ページ数を制限しているのは実行時間が長くなりすぎないようにするためなので、
    # 実際にはもっと多くのページを取得しても良い。
    i = 0
    while search_request and i < max_pages:
        search_response = search_request.execute()
        video_ids = [item['id']['videoId'] for item in search_response['items']]

        # videos.listメソッドで動画の詳細な情報を得る。
        videos_response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()

        yield videos_response['items']

        # list_next()メソッドで次のページを取得するためのリクエスト(次のページがない場合はNone)を得る。
        search_request = youtube.search().list_next(search_request, search_response)
        i += 1


def save_to_mongodb(collection: Collection, items: List[dict]):
    """
    MongoDBのコレクションにアイテムのリストを保存する。

    Args:
        collection (Collection): _description_
        items (List[dict]): _description_
    """
    # MongoDBに保存する前に、後で使いやすいようにアイテムを書き換える。
    for item in items:
        item['_id'] = item['id']

        # statisticsに含まれるviewCountプロパティなどの値が文字列になっているので、数値に変換する。
        for key, value in item['statistics'].items():
            item['statistics'][key] = int(value)

    # 単純にcollection.insert_many()を使うと_idが重複した場合エラーになる。
    # 代わりにcollection.bulk_write()で複数のupsert(insert or update)をまとめて行う。
    operations = [ReplaceOne({'_id': item['_id']}, item, upsert=True) for item in items]
    result = collection.bulk_write(operations)
    logging.info(f'Upseted {result.upserted_count} documents.')


def show_top_videos(collection: Collection):
    """
    MongoDBのコレクション内でビュー数の上位5件を表示する。

    Args:
        collection (Collection): _description_
    """
    for item in collection.find().sort('statistics.viewCount', DESCENDING).limit(5):
        print(item['statistics']['viewCount'], item['snippet']['title'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
