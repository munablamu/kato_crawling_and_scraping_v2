# NOTE: pyppeteerの開発が停止しているため、実行不能
import asyncio
from pyppeteer import launch


async def main():
    # browser = await launch()
    # デフォルトはヘッドレスモードだが、画面を表示するには次の行のようにする。
    browser = await launch(headless=False)

    # Googleのトップ画面を開く。
    page = await browser.newPage()
    await page.goto('https://www.google.co.jp/')

    # タイトルに'Google'が含まれていることを確認する。
    assert 'Google' in (await page.title())

    # 検索語を入力する。
    input_element = await page.querySelector('[name="q"]')
    await input_element.type('Python')

    # フォームを送信してページ遷移するのを待つ。
    await asyncio.wait([
        input_element.press('Enter'),
        page.waitForNavigation(),
    ])

    # タイトルに'Python'が含まれていることを確認する。
    assert 'Python' in (await page.title())

    # スクリーンショットを撮る。
    await page.screenshot({'path': 'search_results.png'})

    # 検索結果を表示する。
    for h3 in await page.querySelectorAll('a > h3'):
        # page.evaluateは、第2引数のオブジェクトを引数に渡して第1引数の関数をJavaScriptとして実行し、
        # その戻り値を取得するメソッド。
        text = await page.evaluate('(e) => e.textContent', h3) # h3のテキストを取得する。
        print(text)
        a = await page.evaluateHandle('(e) => e.parentElement', h3) # h3の親要素を取得する。
        url = await page.evaluate('(e) => e.href', a) # aのhref属性を取得する。
        print(url)

    await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
