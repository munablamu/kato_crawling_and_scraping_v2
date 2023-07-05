import time
import logging
from typing import Iterator

import requests
import lxml.html
import boto3

# S3のバケット名。
S3_BUCKET_NAME = 'scraping-learning'


def main():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(S3_BUCKET_NAME)

    # Wikimedia Commonsのページから画像のURLを抽出する。
    session = requests.Session()
    response = session.get('https://commons.wikimedia.org/wiki/Category:Mountain_glaciers')
    image_urls = scrape_image_urls(response)

    for image_url in image_urls:
        time.sleep(2)

        # 画像ファイルをダウンロードする。
        logging.info(f'Downloading {image_url}')
        response = session.get(image_url)

        # URLからファイル名('/'で区切った一番右側の部分)を取得する。
        _, filename = image_url.rsplit('/', maxsplit=1)

        # ダウンロードしたファイルをS3に保存する。
        logging.info(f'Putting {filename}')
        bucket.put_object(Key=filename, Body=response.content)


def scrape_image_urls(response: requests.Response) -> Iterator[str]:
    """
    引数のレスポンスのページから、サムネイル画像の元画像のURLをyieldする。

    Args:
        response (requests.Response): _description_

    Yields:
        Iterator[str]: _description_
    """
    html = lxml.html.fromstring(response.text)
    for img in html.cssselect('.thumb img'):
        thumbnail_url = img.get('src')
        yield get_original_url(thumbnail_url)


def get_original_url(thumbnail_url: str) -> str:
    """
    サムネイルのURLから元画像のURLを取得する。

    Args:
        thumbnail_url (str): _description_

    Returns:
        str: _description_
    """
    # 一番最後の/で区切り、ディレクトリに相当する部分のURLを得る。
    directory_url, _ = thumbnail_url.rsplit('/', maxsplit=1)
    # /thumb/を/に置き換えて元画像のURLを得る。
    original_url = directory_url.replace('/thumb/', '/')
    return original_url


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
