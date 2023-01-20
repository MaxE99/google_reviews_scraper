from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions 
from seleniumwire import webdriver
from seleniumwire.utils import decode
import re
import sys
import unidecode
import json
import csv

class GoogleReviewsScraper:
    search_term = None
    driver = None
    header = ['reviwer_name', 'review_content', 'full_review_link', 'rating', 'review_time_information', 'owner_reply', 'owner_reply_text']

    def __init__(self, search_term, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_term = self.slugify(search_term)
        self.driver = self.set_driver()

    def slugify(self, search_term):
        slugified_search_term = unidecode.unidecode(search_term).lower()
        return re.sub(r'[\W_]+', '-', slugified_search_term)

    def set_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--ignore-certificate-errors')
        options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
        return webdriver.Chrome(options=options)

    def bypass_consent_page(self):
        if self.driver.current_url.startswith("https://consent.google.com/"):
            WebDriverWait(self.driver, 5).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".VtwTSb form:first-of-type button"))).click()
            print("consent page bypassed...")

    def check_reviews_link_clickable(self):
        def check_condition(self):
            if len(self.find_elements(By.CSS_SELECTOR, '.LBgpqf .dmRWX .mmu3tf span:last-of-type')) > 0:
                self.find_element(By.CSS_SELECTOR, ".LBgpqf .dmRWX .mmu3tf span:last-of-type").click()
                return True
            elif len(self.find_elements(By.CSS_SELECTOR, '.kA9KIf .PPCwl .jANrlb .HHrUdb')) > 0:
                self.find_element(By.CSS_SELECTOR, ".kA9KIf .PPCwl .jANrlb .HHrUdb").click()
                return True
            return False
        return check_condition

    def open_reviews(self):
        WebDriverWait(self.driver, 5).until(self.check_reviews_link_clickable())
        print("Reviews page opened...")

    def scroll_to_bottom(self):
        WebDriverWait(self.driver, 5).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".aIFcqe  .WNBkOb .dS8AEf")))
        scrollbar = self.driver.find_element(By.CSS_SELECTOR, ".aIFcqe  .WNBkOb .dS8AEf")
        total_number_of_reviews_text = self.driver.find_element(By.CSS_SELECTOR, ".PPCwl .Bd93Zb .jANrlb .fontBodySmall").get_attribute('innerText')
        total_number_of_reviews = int(total_number_of_reviews_text.split()[0])
        nr_of_loaded_reviews = len(self.driver.find_elements(By.CSS_SELECTOR, ".aIFcqe  .WNBkOb .dS8AEf .m6QErb .jftiEf"))
        while True:
            if total_number_of_reviews <= nr_of_loaded_reviews:
                break
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollbar)
            if nr_of_loaded_reviews != len(self.driver.find_elements(By.CSS_SELECTOR, ".aIFcqe  .WNBkOb .dS8AEf .m6QErb .jftiEf")):
                nr_of_loaded_reviews = len(self.driver.find_elements(By.CSS_SELECTOR, ".aIFcqe  .WNBkOb .dS8AEf .m6QErb .jftiEf"))
                print(f"{nr_of_loaded_reviews} of {total_number_of_reviews} reviews have been loaded.")

    def get_reviews_from_requests(self):
        reviews = []
        for request in self.driver.requests:
            if request.response and request.response.status_code == 200 and str(request.url).startswith("https://www.google.com/maps/preview/review/listentitiesreviews"): 
                try:
                    body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                    decoded_body = body.decode("utf8")
                    data = json.loads(decoded_body[4:])
                    for i in range(len(data[2])):
                        reviewer_name = data[2][i][0][1]
                        review_time_information = data[2][i][1]
                        rating = data[2][i][4]
                        review_content = data[2][i][3]
                        full_review_link = data[2][i][18]
                        if data[2][i][9] == None:
                            owner_reply = False
                            owner_reply_text = ""
                        else:
                            owner_reply = True
                            owner_reply_text = data[2][i][9][1]
                        review = [reviewer_name, review_content, full_review_link, rating, review_time_information, owner_reply, owner_reply_text]
                        reviews.append(review)
                except:
                    continue
        return reviews

    def write_to_csv(self, reviews):
        with open(f'{self.search_term} - Google Reviews', 'w', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.header)
            writer.writerows(reviews)

    def run(self):
        try:
            self.driver.get(f"https://www.google.com/maps/search/{self.search_term}")
            print("Scraping started...")
            self.bypass_consent_page()
            self.open_reviews()
            self.scroll_to_bottom()
            reviews = self.get_reviews_from_requests()
            self.write_to_csv(reviews)
        except:
            print("Scraping failed! Possible reasons:")
            print("1.The company you were looking for was not found.")
            print("2.Google either changed the layout of the page or the CSS class names.")
            print("3.Google changed the design of the API response.")
            print("4.Network related issues.")
            print("Tip: comment out options.add_argument('headless') to see what happens in the browser.")


if __name__ == '__main__':
    GoogleReviewsScraper(sys.argv[1]).run()