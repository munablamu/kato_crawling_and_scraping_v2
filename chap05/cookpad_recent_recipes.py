# MechanicalSoupでうまくいかなかったので、Seleniumで代用
import os
import time
import logging

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

SLEEP_TIME = 2
# 認証の情報は環境変数から取得する。
COOKPAD_LOGIN = os.environ['COOKPAD_LOGIN']
COOKPAD_PASSWORD = os.environ['COOKPAD_PASSWORD']


def main():
    try:
        options = ChromeOptions()
        options.headless = True
        service = Service(ChromeDriverManager().install())
        driver = Chrome(service=service, options=options) # ChromeのWebDriverオブジェクトを作成する。

        logging.info('Navigating...')
        # Googleのトップ画面を開く。
        driver.get('https://cookpad.com/identity/session/new')

        # タイトルに'Google'が含まれていることを確認する。
        assert 'クックパッド' in driver.title

        # ログインフォーム(class="login_form"の要素内にあるform)を埋める。
        identifier_input = driver.find_element(By.NAME, 'identifier')
        identifier_input.send_keys(COOKPAD_LOGIN)
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(COOKPAD_PASSWORD)

        # フォームを送信する。
        logging.info('Signing in ...')
        login_button = driver.find_element(By.CLASS_NAME, 'submit_button_wrapper')
        login_button.click()
        time.sleep(SLEEP_TIME)

        # クックパッドのトップページが表示されていることを確認する。
        assert 'レシピ検索No.1／料理レシピ載せるなら クックパッド' in driver.title

        # 最近見たレシピのページに移動
        driver.get('https://cookpad.com/recipe/history')
        time.sleep(SLEEP_TIME)
        assert '最近見たレシピ' in driver.title

        # 最近見たレシピの名前とURLを表示する。
        for recipe_element in driver.find_elements(By.CLASS_NAME, 'recipe-preview'):
            a_element = recipe_element.find_element(By.CSS_SELECTOR, 'h2 > a')
            print(a_element.text)
            print(a_element.get_attribute('href'))

    finally:
        driver.quit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
