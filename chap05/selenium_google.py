from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = ChromeOptions()
# ヘッドレスモードを有効にするには、次の行のコメントアウトを解除する。
# options.headless = True
service = Service(ChromeDriverManager().install())
driver = Chrome(service=service, options=options) # ChromeのWebDriverオブジェクトを作成する。

# Googleのトップ画面を開く。
driver.get('https://www.google.co.jp/')

# タイトルに'Google'が含まれていることを確認する。
assert 'Google' in driver.title

# 検索語を入力して送信する。
input_element = driver.find_element(By.NAME, 'q')
input_element.send_keys('Python')
input_element.send_keys(Keys.RETURN)

# タイトルに'python'が含まれていることを確認する。
assert 'Python' in driver.title

# スクリーンショットを撮る。
driver.save_screenshot('search_results.png')

# 検索結果を表示する。
for h3 in driver.find_elements(By.CSS_SELECTOR, 'a > h3'):
    a = h3.find_element(By.XPATH, '..')
    print(h3.text)
    print(a.get_attribute('href'))
