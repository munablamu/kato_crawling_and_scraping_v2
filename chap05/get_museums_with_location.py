import os
import dbm
import json
import logging
from typing import Iterator, Tuple, Union

import requests
from SPARQLWrapper import SPARQLWrapper

YAHOO_GEOCODER_API_URL = 'https://map.yahooapis.jp/geocode/V1/geoCoder'
YAHOO_APPLICATION_ID = os.environ['YAHOO_APPLICATION_ID']
# DBM(ファイルを使ったキーバリュー型のDB)をジオコーディング結果のキャッシュとして使用する。
# この変数はdictと同じように扱うことができ、設定した値はファイルに保存される。
geocoding_cache = dbm.open('geocoding.db', 'c')


def main():
    """
    メインの処理。SPARQLで日本の美術館を取得してGeoJSONファイルに書き出す。
    位置情報がない場合はジオコーディングして取得する。
    """
    features= [] # 美術館の情報を格納するためのリスト。

    for museum in get_museums():
        label = museum.get('label', museum['s']) # ラベルがある場合はラベルを、ない場合はsの値を取得。
        address = museum['address']

        if 'lon_degree' in museum:
            # 位置情報が含まれる場合は、軽度と緯度を60進数(度分秒)から10進数に変換する。
            lon, lat = sexagesimal_to_decimal(museum)
        else:
            # 位置情報が含まれない場合は、住所をジオコーディングして軽度と緯度を取得する。
            lon, lat = geocode(address)

        print(label, address, lon, lat) # 変数の値を表示。

        if lon is None:
            continue # ジオコーディングしても位置情報を取得できなかった場合はfeaturesに含めない。

        # featuresに美術館の情報をGeoJSONのFeatureの形式で追加する。
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': {'label': label, 'address': address},
        })

    # GeoJSONのFeatureCollectionの形式でdictを作成する。
    feature_collection = {
        'type': 'FeatureCollection',
        'features': features,
    }
    # FeatureCollectionを.geojsonという拡張子のファイルに書き出す。
    with open('museums.geojson', 'w') as f:
        json.dump(feature_collection, f)


def get_museums() -> Iterator[dict]:
    """
    SPARQLを使ってDBpedia Japaneseから美術館の情報を取得する。
    """
    logging.info('Executing SPARQL query...')

    # SPARQLエンドポイントのURLを指定してインスタンスを作成する。
    sparql = SPARQLWrapper('http://ja.dbpedia.org/sparql')
    # 日本の美術館を取得するクエリを設定する。
    sparql.setQuery(r"""
SELECT * WHERE {
                    ?s rdf:type dbo:Museum ;
                    prop-ja:所在地 ?address .
                    OPTIONAL { ?s rdfs:label ?label . }
                    OPTIONAL {
                    ?s prop-ja:経度度 ?lon_degree ;
                       prop-ja:経度分 ?lon_minute ;
                       prop-ja:経度秒 ?lon_second ;
                       prop-ja:緯度度 ?lat_degree ;
                       prop-ja:緯度分 ?lat_minute ;
                       prop-ja:緯度秒 ?lat_second .
                    }
                    FILTER REGEX(?address, "^\\p{Han}{2,3}[都道府県]")
                } ORDER BY ?s
""")
    sparql.setReturnFormat('json')
    # query()でクエリを実行し、convert()でレスポンスをパースしてdictを得る。
    response = sparql.query().convert()

    logging.info(f'Got {len(response["results"]["bindings"])} results.')

    # クエリの実行結果を反復処理する。
    for result in response['results']['bindings']:
        # 扱いやすいように {変数名1: 値1, 変数名2: , ...}という形式のdictをyieldする。
        # resultを加工した辞書を得るために、辞書内包表記を使う。
        yield {name: binding['value'] for name, binding in result.items()}


def sexagesimal_to_decimal(museum: dict) -> Tuple[float, float]:
    """
    60進数(度分秒)の経度と緯度を10進数に変換する。
    """
    # 10進数の度 = 60進数の度 + 60進数の分 / 60 + 60進数の秒 / 3600
    lon = float(museum['lon_degree']) + float(museum['lon_minute']) / 60 + \
        float(museum['lon_second']) / 3600
    lat = float(museum['lat_degree']) + float(museum['lat_minute']) / 60 + \
        float(museum['lat_second']) / 3600

    return (lon, lat)


def geocode(address: str) -> Union[Tuple[float, float], Tuple[None, None]]:
    """
    引数で指定した住所をYahoo!ジオコーダAPIでジオコーディングして、経度と緯度のペアを返す。
    """
    if address not in geocoding_cache:
        # 住所がキャッシュに存在しない場合はYahoo!ジオコーダAPIでジオコーディングする。
        logging.info(f'Geocoding {address}...')
        r = requests.get(YAHOO_GEOCODER_API_URL, params={
            'appid': YAHOO_APPLICATION_ID,
            'output': 'json',
            'query': address,
        })

        # APIのレスポンスをキャッシュ(DBM)に格納する。
        # DBMのキーや値にはbytes型しか使えないが、str型は自動的にbytes型に変換される。
        geocoding_cache[address] = r.content

    # キャッシュ内のAPIレスポンスをdictに変換する。値はbytes型なので、文字列として扱うにはデコードが必要。
    response = json.loads(geocoding_cache[address].decode('utf-8'))

    if 'Feature' not in response:
        return (None, None) # ジオコーディングで結果が得られなかった場合はNoneのペアを返す。

    # Coordinatesというキーの値を,で分割。
    coordinates = response['Feature'][0]['Geometry']['Coordinates'].split(',')
    return (float(coordinates[0]), float(coordinates[1]))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
