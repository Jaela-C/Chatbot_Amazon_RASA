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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
import time


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_ask_amazon"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        product_value = tracker.get_slot("product")
        # dispatcher.utter_message(text="test: " + str(product_value))

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
                    result += f'{result_found[item][0]}\n Precio: ${result_found[item][1]}\n\n'
                else:
                    break
            return dispatcher.utter_message(result)


        def amazon(browser, search_txt):
            result_found, result_prices = collections.defaultdict(list), {}
            try:
                browser.get('https://www.amazon.com/-/es/')
                browser.find_element(by=By.ID, value="twotabsearchtextbox").send_keys(search_txt)
                browser.find_element(by=By.ID, value="nav-search-submit-button").click()

                items = wait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))

                for num, item in enumerate(items, 1):
                    # nombre
                    name = item.find_element(by=By.XPATH, value='.//span[@class="a-size-medium a-color-base a-text-normal"]')

                    # link
                    link = item.find_element(by=By.XPATH, value='.//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute("href")
                    a_link = f'<a href={link} target="_blank" style="color:#FFFFFF;">{name.text[:30] + "..."}</a>'
                    result_found[num].append(a_link)

                    # precio
                    if is_exists(item, './/span[@class="a-price-whole"]') and is_exists(item, './/span[@class="a-price-fraction"]'):
                        whole_price = item.find_element(by=By.XPATH, value='.//span[@class="a-price-whole"]')
                        fraction_price = item.find_element(by=By.XPATH, value='.//span[@class="a-price-fraction"]')
                        price = float(whole_price.text.replace(",", "") + "." + fraction_price.text)
                        result_prices[num] = price
                    else:
                        price = 'Sin precio'
                    result_found[num].append(price)
                return result_prices, result_found
            except:
                return {}, {}


        def ebay(browser, search_txt):
            result_found, result_prices = collections.defaultdict(list), {}
            try:
                browser.get('https://ec.ebay.com/')
                browser.find_element(by=By.XPATH, value='//*[@id="gh-ac"]').send_keys(search_txt)
                browser.find_element(by=By.XPATH, value='//*[@id="gh-btn"]').click()

                items = wait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//ul[contains(@class, "srp-results srp-list clearfix")]/li')))

                for num, item in enumerate(items, 1):

                    if is_exists(item, './/h3[@class="s-item__title"]/span[@class="LIGHT_HIGHLIGHT"]'):
                        continue

                    if 'nuevo' not in item.find_element(by=By.XPATH, value='.//span[@class="SECONDARY_INFO"]').text.lower():
                        continue

                    # nombre
                    name = item.find_element(by=By.XPATH, value='.//h3[@class="s-item__title"]')

                    # link
                    link = item.find_element(by=By.XPATH, value='.//a[@class="s-item__link"]').get_attribute("href")
                    a_link = f'<a href={link} target="_blank" style="color:#FFFFFF;">{name.text[:30] + "..."}</a>'
                    result_found[num].append(a_link)

                    # precio
                    if is_exists(item, './/span[@class="s-item__price"]'):
                        whole_price = item.find_element(by=By.XPATH, value='.//span[@class="s-item__price"]')
                        print(whole_price.text)
                        price = float(whole_price.text.replace("USD", "").replace(" ", "").split(" a ")[-1])
                        result_prices[num] = price
                    else:
                        price = 'Sin precio'
                    result_found[num].append(price)

                return result_prices, result_found
            except:
                return {}, {}


        def alibaba(browser, search_txt):
            result_found, result_prices = collections.defaultdict(list), {}
            try:

                browser.get('https://spanish.alibaba.com/')
                browser.find_element(by=By.CLASS_NAME, value='ui-searchbar-keyword').send_keys(search_txt)
                browser.find_element(by=By.CLASS_NAME, value='ui-searchbar-keyword').send_keys(Keys.ENTER)

                items = wait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "organic-list app-organic-search__list")]/div[@class="list-no-v2-outter J-offer-wrapper"]')))

                for num, item in enumerate(items, 1):

                    # nombre
                    name = item.find_element(by=By.XPATH, value='.//P[@class="elements-title-normal__content large"]')

                    # link
                    link = item.find_element(by=By.XPATH, value='.//a[@class="elements-title-normal one-line"]').get_attribute("href")
                    a_link = f'<a href={link} target="_blank" style="color:#FFFFFF;">{name.text[:30] + "..."}</a>'
                    result_found[num].append(a_link)

                    # precio
                    if is_exists(item, './/span[@class="elements-offer-price-normal__promotion"]'):
                        whole_price = item.find_element(by=By.XPATH, value='.//span[@class="elements-offer-price-normal__promotion"]')
                        price = float(whole_price.text.replace("$", "").replace(".", "").replace(",", ".").split("-")[-1])
                        result_prices[num] = price
                    else:
                        price = 'Sin precio'
                    result_found[num].append(price)

                return result_prices, result_found
            except:
                return {}, {}


        def main(search_txt):
            browser = webdriver.Chrome(service=Service(r'C:\ChromeDriver\chromedriver.exe'))
            try:
                result_prices_1, result_found_1 = amazon(browser, search_txt)
                time.sleep(2)
                result_prices_2, result_found_2 = ebay(browser, search_txt)
                time.sleep(2)
                result_prices_3, result_found_3 = alibaba(browser, search_txt)
                time.sleep(2)
                sort_result_prices = OrderedDict(sorted({**result_prices_1, **result_prices_2, **result_prices_3}.items(), key=lambda x: x[1]))
                return get_str_sort_prices(sort_result_prices, {**result_found_1, **result_found_2, **result_found_3})
            except:
                return 'Lo sentimos, ha ocurrido un error, intente de nuevo.'
            finally:
                browser.quit()

        main(str(product_value))

        return []
