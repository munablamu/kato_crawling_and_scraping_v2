import sys
import hashlib
import json
import logging

from elasticsearch import Elasticsearch


def main():
    """
    メインとなる処理。
    """
    # Elasticsearchのクライアントを作成する。
    # 第1引数でノードのリストを指定できる。デフォルトではlocalhostの9200ポートに接続するため省略可能。
    es = Elasticsearch(['http://localhost:9200'])
    create_pages_index(es) # pagesインデックスrを作成。

    for line in sys.stdin: # 標準入力から1行ずつ読み込む。
        page = json.loads(line) # 読み込んだ行をJSONとしてパースする。
        # ドキュメントIDとして、URLのSHA-1ダイジェストを使用する。
        doc_id = hashlib.sha1(page['url'].encode('utf-8')).hexdigest()
        # pagesインデックスrにインデックス化（保存）する。
        es.index(index='pages', id=doc_id, body=page)


def create_pages_index(es: Elasticsearch):
    """
    Elasticsearchにpagesインデックスを作成する。

    Args:
        es (Elasticsearch): _description_
    """
    # キーワード引数bodyでJSONに相当するdictを指定する。
    # ignore=400はインデックスが存在する場合でもエラーにしないという意味。
    es.indices.create(index='pages', ignore=400, body={
        # settingsという項目で、kuromoji_analyzerというアナライザーを定義する。
        # アナライザーはテンテインデックスの作成方法を指定するもの。
        'settings': {
            'analysis': {
                'analyzer': {
                    'kuromoji_analyzer': {
                        # 日本語形態素解析を使って文字列を分解するkuromoji_tokenizerを使用。
                        'tokenizer': 'kuromoji_tokenizer'
                    }
                }
            }
        },
        # mappingsという項目で、ドキュメントが持つフィールドを定義する。
        'mappings': {
            '_doc': {
                # url, title, contectの3つのフィールドを定義。
                # titleとcontentではアナライザーとして上で適宜したkuromoji_analyzerを使用。
                'properties': {
                    'url': {'type': 'text'},
                    'title': {'type': 'text', 'analyzer': 'kuromoji_analyzer'},
                    'content': {'type': 'text', 'analyzer': 'kuromoji_analyzer'}
                }
            }
        }
    })


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # INFOレベル以上のログを出力するよう設定する。
    main()
