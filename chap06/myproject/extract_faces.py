import sys
import logging
from pathlib import Path
from typing import Iterator

import cv2
from numpy import array


def main():
    """
    メインとなる処理.
    """
    # 顔画像の出力先のディレクトリが存在なしな場合は作成しておく。
    output_dir = Path('faces')
    output_dir.mkdir(exist_ok=True)
    # 特徴量ファイルのパスを指定して、分類器オブジェクトを作成する。
    classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
    # コマンドライン引数のファイルパスについて反復処理する.
    for image_path in sys.argv[1:]:
        process_image(classifier, Path(image_path), output_dir)


def process_image(classifier: cv2.CascadeClassifier, image_path: Path, output_dir: Path):
    """
    1つの画像ファイルを処理する. 画像から排出した顔画像ファイルに保存する.

    Args:
        classifier (cv2.CascadeClassifier): _description_
        image_path (Path): _description_
        output_dir (Path): _description_
    """
    logging.info(f'Processing {image_path}...')
    image = cv2.imread(str(image_path)) # 引数のパスの画像ファイルを読み込む.
    if image is None:
        # 画像ファイルが存在しない場合はエラーを表示して終了する.
        logging.error(f'Image "{image_path}" not found.')
        exit(1)

    face_images = extract_faces(classifier, image)

    for i, face_image in enumerate(face_images):
        # 出力先のファイルパスを組み立てる. stemはファイル名の拡張子を除いた部分を表す.
        output_path = output_dir.joinpath(f'{image_path.stem}_{i}.jpg')
        # 顔の画像を保存する.
        cv2.imwrite(str(output_path), face_image)


def extract_faces(classifier: cv2.CascadeClassifier, image: array) -> Iterator[array]:
    """
    画像から顔を検出して, 顔の部分を切り取った画像をyieldする.

    Args:
        classifier (cv2.CascadeClassifier): _description_
        image (array): _description_

    Yields:
        Iterator[array]: _description_
    """
    # 顔検出を高速化するため, 画像をグレースケールに変換する.
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 顔を検出する.
    faces = classifier.detectMultiScale(gray_image)
    # 検出した顔のリストについて反復処理する.
    for x, y, w, h in faces:
        yield image[y:y+h, x:x+w]


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
