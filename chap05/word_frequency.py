import sys
import logging
from collections import Counter
from pathlib import Path
from typing import List, Iterator, TextIO # TextIOはstrを取得できるファイルオブジェクトを表す型

import MeCab

tagger = MeCab.Tagger('')
tagger.parse('') # これは.parseToNode()の不具合を回避するためのハック。


def main():
    """
    コマンドライン引数で指定したディレクトリ内のファイルを読み込んで、頻出単語を表示する。
    """
    # コマンドラインの第1引数で、WikiExtractorの出力先のディレクトリを指定する。
    # Pathオブジェクトはファイルやディレクトリのパス操作を抽象化するオブジェクト。
    input_dir = Path(sys.argv[1])

    # 単語の出現回数を格納するCounterオブジェクトを作成する。
    # Counterクラスはdictを継承しており、値としてキーの出現回数を確保する。
    frequency = Counter()

    # .glob()でワイルドカードにマッチするファイルのリストを取得し、マッチしたすべてのファイルを処理する。
    for path in sorted(input_dir.glob('*/wiki_*')):
        logging.info(f'Processing {path}...')

        with open(path) as file:
            # ファイルに含まれる記事内の単語の出現回数を数え、出現回数をマージする。
            frequency += count_words(file)

    # 全記事の処理が完了したら、上位30件の名詞と出現回数を表示する。
    for word, count in frequency.most_common(30):
        print(word, count)


def count_words(file: TextIO) -> Counter:
    """
    WikiWExtractorが出力したファイルに含まれるすべての記事から単語の出現回数を数える関数。

    Args:
        file (TextIO): _description_

    Returns:
        Counter: _description_
    """
    frequency = Counter() # ファイル内の単語の出現頻度を数えるCounterオブジェクト
    num_docs = 0 # ログ出力用に、処理した記事数を数えるための変数。

    for content in iter_doc_contents(file): # ファイル内の全記事について反復処理する。
        words = get_words(content) # 記事に含まれる名詞のリストを取得する。
        # Counterのupdate()メソッドにリストなどの反復可能オブジェクトを指定すると、
        # リストに含まれる値の出現回数を一度に増やせる。
        frequency.update(words)
        num_docs += 1

    logging.info(f'Found {len(frequency)} words from {num_docs} documents.')
    return frequency


def iter_doc_contents(file: TextIO) -> Iterator[str]:
    """
    ファイルイブジェクトを読み込んで、記事の中身(開始タグ<doc...>と終了タグ</doc>の間のテキスト>を
    順に返すジェネレーター関数。

    Args:
        file (TextIO): _description_

    Yields:
        Iterator[str]: _description_
    """
    for line in file: # ファイルに含まれるすべての行について反復処理する。
        if line.startswith('<doc '):
            buffer = [] # 開始タグが見つかったらバッファを初期化する。
        elif line.startswith('</doc>'):
            # 終了タグがみつかたらバッファの中身を結合してyieldする。
            content = ''.join(buffer)
            yield content
        else:
            buffer.append(line) # 開始タグ・終了タグ以外の行はバッファに追加する。


def get_words(content: str) -> List[str]:
    """
    文字列内に出現する名詞のリスト(重複含む)を取得する関数。

    Args:
        content (str): _description_

    Returns:
        List[str]: _description_
    """
    words = [] # 出現した名詞を格納するリスト。

    node = tagger.parseToNode(content)
    while node:
        # node.featureはカンマで区切られた文字列なので、split()で分割して
        # 最初の2項目をposとpos_sub1に代入する。posはPart of Speech(品詞)の略。
        pos, pos_sub1 = node.feature.split(',')[:2]
        # 固有名詞または一般名詞の場合のみwordsに追加する。
        if pos == '名詞' and pos_sub1 in ('固有名詞', '一般'):
            words.append(node.surface)
        node = node.next

    return words


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
