import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome import options
import constants as CONSTANTS
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from concurrent.futures.thread import ThreadPoolExecutor
import urllib.request
import os
from pathlib import Path

chrome_options = Options()
class ScrapAnimalKingdom:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_script_timeout(20)
        self.driver.set_page_load_timeout(20)
        self.active_category = None
        self.active_url = None
        self.active_animal = None
        self.extract_total_number = lambda string : string.split('(')[1].replace(")", "")
        self.active_page = {
            'next_page_href':None,
            'page_members_div': None,
            'total_number':0,
            'page_members':[]
        }

        self.executor = ThreadPoolExecutor(10)
    
    def init_page(self):
        self.active_page['next_page_href'] = self.driver.find_elements(By.CLASS_NAME, 'category-page__pagination-next')[0].get_attribute('href')
        self.active_page['page_members_div'] = self.driver.find_element(By.ID, 'content')
        self.active_page['total_number'] = self.extract_total_number(self.driver.find_element(By.CLASS_NAME, 'category-page__total-number').text)
        cat_page_members = self.active_page['page_members_div'].find_elements(By.TAG_NAME, "li")
        get_name = lambda i : cat_page_members[i].find_element(By.TAG_NAME, 'a').get_attribute('title')
        get_link = lambda i : cat_page_members[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
        self.active_page['page_members'] = [
                {
                    'name': get_name(index),
                    'link': get_link(index)
                }
            for index in range(len(cat_page_members)) if get_link(index) is not None and get_name(index) is not None]
        
        # print(next_page_href.text, total_number.text, len(page_members))
    def set_active_category(self, category):
        self.active_category = category
        self.active_url = f"{CONSTANTS.BASE_URL}/wiki/Category:{self.active_category}"
        
    def get_headline_details(self):
        headlines = ['h2', 'h3', 'h4', 'h5', 'h6']
        topic_details = []
        for h in headlines:
            topics_details_elem = self.driver.find_elements(By.CSS_SELECTOR, f'.mw-parser-output {h} + p')
            if len(topics_details_elem) <= 0:
                break
            topic_details.extend([elem.text for elem in topics_details_elem])
        return topic_details

    def get_animal_details(self):
        try:
            category_div = self.driver.find_element(By.CLASS_NAME, 'categories')
            category_list = category_div.find_elements(By.TAG_NAME, 'li')
            categories = [categ.get_attribute('data-name') for categ in category_list if categ.get_attribute('data-name') is not None]
            print("="*20+"Categories"+"="*20)
            print(categories)
        except Exception as e:
            print(f"No categories for {self.active_url}")
        # recursively get the topic sub topic details

        # get initital topics
        try:
            topics_el = self.driver.find_elements(By.CLASS_NAME, 'mw-headline')
            topics_titles = [el.text for el in topics_el]
            
            initial_topics = dict(zip(topics_titles, self.get_headline_details()))
            print("="*20+"Initital topics"+"="*20)
            print(initial_topics)
        except Exception as e:
            print("no initital topics either")

        # get description
        try:
            description = []
            actual_descr_div = self.driver.find_element(By.CLASS_NAME, "mw-parser-output")
            for el in actual_descr_div.find_elements(By.XPATH, ".//*"):
                if el.tag_name == 'p':
                    description.append(el.text)
                if el.tag_name == 'h2':
                    break
            print("="*20+"Description"+"="*20)
            print(description)
            print("*"*20)
        except Exception as e:
            print("Couldnt get description")

        # get classification
        try:
            div = self.driver.find_element(By.CLASS_NAME, "mw-parser-output")
            table = self.driver.find_element(By.CSS_SELECTOR, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            img_src = rows[1].find_element(By.TAG_NAME, "img").get_attribute("src")
            file_name = f'{self.active_category}_{self.active_animal.replace(" ", "_")}'
            urllib.request.urlretrieve(img_src, f"imgs/{file_name}.jpeg")
            classification = {}
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) > 1:
                    classification.update({tds[0].text:tds[1].text})
            
            status = rows[-1].text

            print("="*20+"Classification"+"="*20)
            print(classification, status)
        except Exception as e:
            print("Couldn't get classification", e)

    def find_animal_category_details(self):
        print(f"Ready: finding {self.active_category}")
        self.init_page()
        time.sleep(2)
        print(self.active_page['total_number'], len(self.active_page['page_members']), self.active_page['page_members'][0])
        loop = asyncio.get_event_loop()
        index = 0
        while index < len(self.active_page['page_members']):
            self.active_url = self.active_page['page_members'][index]['link']
            self.active_animal = self.active_page['page_members'][index]['name']
            time.sleep(1)
            self.open_active_link(self.get_animal_details)
            remaining = len(self.active_page["page_members"]) - index
            print(index, f"{remaining} to go")
            index += 1
        else:
            time.sleep(1)
            index = 0
            self.active_url = self.active_page['next_page_href']
            print(self.active_url)
            self.open_active_link(self.find_animal_category_details)

        # for i in range(len(self.active_page['page_members'][:3])):
        #     self.active_url = self.active_page['page_members'][i]['link']
        #     self.active_animal = self.active_page['page_members'][i]['name']
        #     time.sleep(2)
        #     self.open_active_link(self.get_animal_details)
            

    def open_active_link(self, callback):
        try:
            self.driver.get(self.active_url)

            print(f"Scrapping {self.active_url}")
            callback()
        except:
            print(f"Stop loadiing! {self.active_url} took too long to resolve")
            time.sleep(1)
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            callback()
            
            
if __name__ == '__main__':
    scrapper = ScrapAnimalKingdom()
    scrapper.set_active_category(CONSTANTS.CLASSES['vertebrates']['Birds'])
    scrapper.open_active_link(scrapper.find_animal_category_details)
