import time
from selenium import webdriver
from selenium.webdriver.chrome import options
import constants as CONSTANTS
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
class ScrapAnimalKingdom:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_script_timeout(20)
        self.driver.set_page_load_timeout(20)

        self.active_category = CONSTANTS.CLASSES['vertebrates']['Birds']
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
        # get description
        print(self.active_url, "Getting details")
        
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
            # import pdb
            # pdb.set_trace()
            print("="*20+"Initital topics"+"="*20)
            print(initial_topics)
        except Exception as e:
            print("no initital topics either")


        try:
            description = []
            actual_descr_div = self.driver.find_element(By.CLASS_NAME, "mw-parser-output")
            for el in actual_descr_div.find_elements(By.XPATH, ".//*"):
                if el.tag_name == 'p':
                    description.append(el.text)
                if el.tag_name == 'h2':
                    break
        except Exception as e:
            print("Cant get details")

        print("="*20+"Description"+"="*20)
        print(description)
        print("*"*20)
        # print(topics)

    def find_animal_category_details(self):
        print(f"Ready: finding {self.active_category}")

        next_page_href = self.driver.find_element_by_xpath(CONSTANTS.PATHS.get('pagination_xpath'))
        page_members_div = self.driver.find_element_by_xpath(CONSTANTS.PATHS.get('cat_page_mbrs_xpath'))
        total_number = self.driver.find_element_by_xpath(CONSTANTS.PATHS.get('total_number_in_category_xpath'))
        cat_page_members = page_members_div.find_elements(By.TAG_NAME, "li")


        print(next_page_href.text, total_number.text, len(cat_page_members))
        index = 3
        link = cat_page_members[index].find_element(By.XPATH, f'//*[@id="mw-content-text"]/div[3]/div[1]/ul/li[{index}]/a')
        self.active_url = link.get_attribute('href')
        
        self.open_active_link(self.get_animal_details)

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
    scrapper.open_active_link(scrapper.find_animal_category_details)
