# 実行コマンド: foreman run python notify_to_slack.py
import os
import time
from typing import List
import logging

import requests
from mojimoji import zen_to_han
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

SLEEP_TIME = 2
SLACK_INCOMING_WEBHOOK_URL = os.environ['SLACK_INCOMING_WEBHOOK_URL']


def main():
    """
    メインの処理。
    """
    try:
        service = Service(ChromeDriverManager().install())
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(service=service, options=options)

        navigate(driver) # noteのトップページに遷移する。
        contents = scrape_contents(driver) # コンテンツのリストを取得する。
        logging.info(f'Found {len(contents)} contents.')

        # スキの数が最も多いコンテンツを取得する。
        content = sorted(contents, key=lambda c: c['like'], reverse=True)[0]
        logging.info(f'Notifying to Slack: {content["url"]}')
        # 取得したコンテンツのスキの数とURLをSlackに通知する。
        requests.post(SLACK_INCOMING_WEBHOOK_URL, json={
            'text': f':heart: {content["like"]} {content["url"]}',
            'unfurl_links': True, # リンクのタイトルや画像を表示する。
        })

    finally:
        driver.quit()


def navigate(driver: WebDriver):
    """
    目的のページに遷移する。
    """
    logging.info('Navigating...')
    driver.get('https://note.com')
    time.sleep(SLEEP_TIME)
    assert 'note' in driver.title

    scroll_height = driver.execute_script('return document.body.scrollHeight') // 3
    for _ in range(4):
        # 現在のスクロール位置を取得。
        current_position = driver.execute_script('return window.pageYOffset')
        # スクロール位置にスクロールする高さを足す。
        new_position = current_position + scroll_height
        # 新しいスクロール位置までスクロールする。
        driver.execute_script(f'scroll(0, {new_position})')
        logging.info('Waiting for contents to be loaded...')
        time.sleep(SLEEP_TIME)


def scrape_contents(driver: WebDriver) -> List[dict]:
    """
    文章コンテンツのURL、タイトル、概要、スキの吸うを含むdictのリストを取得する。
    """
    contents = []
    #
    horizontal_elements = driver.find_elements(By.CSS_SELECTOR,
                                               '.t-timeline .o-horizontalScrollingNoteList')
    for horizontal_element_i in horizontal_elements:
        for note_element in horizontal_element_i.find_elements(By.CSS_SELECTOR, '.m-largeNoteWrapper'):
            a_element = note_element.find_element(By.CSS_SELECTOR, 'a.m-largeNoteWrapper__link')
            contents.append({
                'url': a_element.get_attribute('href'),
                'title': zen_to_han(a_element.get_attribute('title'), kana=False),
                'user': zen_to_han(note_element.find_element(By.CSS_SELECTOR, '.o-verticalTimeLineNote__user').text, kana=False),
                'like': int(note_element.find_element(By.CSS_SELECTOR, '.o-verticalTimeLineNote__action').text.replace(',', '')),
            })

    return contents


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
