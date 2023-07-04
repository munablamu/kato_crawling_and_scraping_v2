from typing import List

from elasticsearch import Elasticsearch
from bottle import route, run, request, template

es = Elasticsearch(['http://localhost:9200'])


@route('/')
def index():
    """
    / へのリクエストを処理する。
    """
    query = request.query.q # クエリ(?q= の値)を取得する。
    # クエリがある場合は検索結果を、ない場合は[]をpagesに代入する。
    pages = search_pages(query) if query else []
    # bottleのテンプレート機能を使って、search.tplというファイルから読み込んだテンプレートに
    # queryとpagesの値を渡してレンダリングした結果をレスポンスボディとして返す。
    return template('search', query=query, pages=pages)


def search_pages(query: str) -> List[dict]:
    """
    引数のクエリでElasticsearchからWebページを検索し、結果のリストを返す。

    Args:
        query (str): _description_

    Returns:
        List[dict]: _description_
    """
    # Simple Queryを使って検索する。
    result = es.search(index='pages', body={
        'query': {
            'simple_query_string': {
                'query': query,
                'fields': ['title^5', 'content'],
                'default_operator': 'and'
            }
        },
        # contentフィールドでマッチする部分をハイライトするよう設定。
        'highlight': {
            'fields': {
                'content': {
                    'fragment_size': 150,
                    'number_of_fragments': 1,
                    'no_match_size': 150
                }
            }
        }
    })
    # 個々のページを含むリストを返す。
    return result['hits']['hits']


if __name__ == '__main__':
    # 開発用のHTTPサーバーを起動する。
    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
