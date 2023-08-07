import mechanicalsoup
from fake_useragent import UserAgent

ua = UserAgent()
browser = mechanicalsoup.StatefulBrowser(user_agent=str(ua.chrome))
browser.open('https://www.google.co.jp/')

# 検索語を入力して送信する。
browser.select_form('form[action="/search"]')
browser['q'] = 'Python'
browser.submit_selected()

# 検索結果のタイトルとURLを抽出して表示する。
page = browser.get_current_page() # 現在のページのBeautifulSoupオブジェクトを取得する。
for a in page.select('div > div > div > div > div > div > a'):
    print(a.text)
    print(browser.absolute_url(a.get('href')))
