# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from xml.dom.minidom import Identified

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests
import json
import collections
from selenium import webdriver
from collections import OrderedDict
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_ask_amazon"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        product_value = tracker.get_slot("product")
        dispatcher.utter_message(text="test: " + str(product_value))

        # deploy_bot(str(identification_value), str(email_value))
        def is_exists(item, xpath):
            try:
                item.find_element(by=By.XPATH, value=xpath)
            except NoSuchElementException:
                return False
            return True

        def get_str_sort_prices(sort_result_prices, result_found):
            result = ''
            for num, item in enumerate(sort_result_prices.keys()):
                if num < 5:
                    result += f'{result_found[item][0]} Price: ${result_found[item][1]} {result_found[item][2]} '
                else:
                    break
            return dispatcher.utter_message(text=result)
        def main(search_txt):
            result_found, result_prices = collections.defaultdict(list), {}
            browser = webdriver.Chrome(service=Service(r'C:\ChromeDriver\chromedriver.exe'))
            browser.get('https://www.amazon.com/-/es/')
            browser.find_element(by=By.ID, value="twotabsearchtextbox").send_keys(search_txt)
            browser.find_element(by=By.ID, value="nav-search-submit-button").click()

            items = wait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))

            for num, item in enumerate(items, 1):

                name = item.find_element(by=By.XPATH, value='.//span[@class="a-size-medium a-color-base a-text-normal"]')
                result_found[num].append(name.text)

                if is_exists(item, './/span[@class="a-price-whole"]') and is_exists(item, './/span[@class="a-price-fraction"]'):
                    whole_price = item.find_element(by=By.XPATH, value='.//span[@class="a-price-whole"]')
                    fraction_price = item.find_element(by=By.XPATH, value='.//span[@class="a-price-fraction"]')
                    price = float(whole_price.text.replace(",", "") + "." + fraction_price.text)
                    result_prices[num] = price
                else:
                    price = 'Sin precio'
                result_found[num].append(price)

                # ratings = item.find_element(by=By.XPATH, value='.//div[@class="a-row a-size-small"]/span[1]')
                # result_found[num].append(ratings.get_attribute('aria-label') if ratings else '0 de 5 estrellas')

                # ratings_num = item.find_element(by=By.XPATH, value='.//div[@class="a-row a-size-small"]/span[2]')
                # result_found[num].append(str(ratings_num.get_attribute('aria-label')) if ratings else 0)

                link = item.find_element(by=By.XPATH, value='.//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute("href")

                result_found[num].append(link)

            browser.quit()
            sort_result_prices = OrderedDict(sorted(result_prices.items(), key=lambda x: x[1]))
            return get_str_sort_prices(sort_result_prices, result_found)

        main(str(product_value))

        return []
