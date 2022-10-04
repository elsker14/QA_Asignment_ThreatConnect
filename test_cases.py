from typing import Tuple, List
from datetime import datetime, timedelta
from selenium.common import TimeoutException
from selenium.webdriver import Keys, Firefox, ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
import unittest
import re


class WebdriverWrapper:

    def __init__(self):
        self.driver = Firefox(
            service=FirefoxService(
                GeckoDriverManager().install()
            )
        )
        self.driver.maximize_window()

    def get_element_located(self, locator: Tuple[str, str], timeout: float = 10) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located(locator))

    def get_element_clickable(self, locator: Tuple[str, str], timeout: float = 10) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(locator))

    def get_all_elements_located(self, locator: Tuple[str, str], timeout: float = 10) -> List[WebElement]:
        return WebDriverWait(self.driver, timeout).until(ec.presence_of_all_elements_located(locator))

    def get_all_elements_visible(self, locator: Tuple[str, str], timeout: float = 10) -> List[WebElement]:
        return WebDriverWait(self.driver, timeout).until(ec.visibility_of_all_elements_located(locator))


ww = WebdriverWrapper()


class AirBnbTests(unittest.TestCase):
    TEST_URL = 'https://www.airbnb.com/'

    def setUp(self) -> None:
        ww.driver.get(self.TEST_URL)

    def tearDown(self) -> None:
        if ww.driver:
            ww.driver.close()

    def test_automation_assignment(self):
        ##########
        # Step 1 #
        ##########
        ww.get_element_clickable((By.XPATH, '//div[text()="Anywhere"]')).click()
        search_input = ww.get_element_clickable((By.ID, 'bigsearch-query-location-input'))
        search_input.send_keys("Spain" + Keys.DOWN + Keys.ENTER)

        ##########
        # Step 2 #
        ##########
        check_in = datetime.now()
        check_out = check_in + timedelta(days=4)
        ww.get_element_clickable(
            (By.CSS_SELECTOR, f'[data-testid=\"calendar-day-{check_in.strftime("%m/%d/%Y")}\"]')
        ).click()
        ww.get_element_clickable(
            (By.CSS_SELECTOR, f'[data-testid=\"calendar-day-{check_out.strftime("%m/%d/%Y")}\"]')
        ).click()

        ##########
        # Step 3 #
        ##########
        # Check that the days before the current day are disabled
        self.assertTrue(
            ww.get_element_clickable(
                (By.CSS_SELECTOR,
                 f'[data-testid=\"calendar-day-{(check_in - timedelta(days=1)).strftime("%m/%d/%Y")}\"]')
            ).get_attribute('data-is-day-blocked') == 'true'
        )
        check_in_string = check_in.strftime("%B")[:3] + " " + str(check_in.day)
        check_out_string = check_out.strftime("%B")[:3] + " " + str(check_out.day)
        # Check the selected time period
        self.assertTrue(
            ww.get_element_clickable(
                (By.XPATH, '//div[text()="Check in"]/../div[2]')
            ).text == check_in_string
        )
        self.assertTrue(
            ww.get_element_clickable(
                (By.XPATH, '//div[text()="Check out"]/../div[2]')
            ).text == check_out_string
        )

        ##########
        # Step 4 #
        ##########
        ww.get_element_clickable((By.ID, 'tab--tabs--1')).click()
        ww.get_element_clickable((By.ID, 'flexible_trip_lengths-weekend_trip')).click()

        ##########
        # Step 5 #
        ##########
        ww.get_element_clickable((By.ID, 'tab--tabs--0')).click()
        ww.get_element_clickable((By.CSS_SELECTOR, '[data-testid="structured-search-input-search-button"]')).click()
        first_location = ww.get_all_elements_visible((By.CSS_SELECTOR, '[itemprop=itemListElement]'))[0]
        ActionChains(ww.driver).move_to_element(first_location).perform()
        # Check if the price tag is highlighted
        self.assertTrue(
            ww.get_element_clickable(
                (By.XPATH, '//span[text()="selected"]')
            )
        )

        ##########
        # Step 6 #
        ##########
        place_name = ww.get_element_clickable((By.CSS_SELECTOR, 'div[id*=title_]')).text
        price_per_night = re.findall(
            r'\b\d+\b', ww.get_element_clickable(
                (By.XPATH, '//span[contains(text(), "per night")]')
            ).text
        )[0]
        rating = ww.get_element_clickable(
            (By.XPATH, '//span[contains(text(), "per night")]/../../../../../span')
        ).text
        ww.get_element_clickable(
            (By.XPATH, '//span[text()="selected"]/..')
        ).click()
        card_place_name = ww.get_element_clickable((By.CSS_SELECTOR, '._1mhd7uz div[id*=title_]')).text
        card_price_per_night = re.findall(
            r'\b\d+\b', ww.get_element_clickable(
                (By.XPATH, '//div[@class="_1mhd7uz"]//span[contains(text(), "per night")]')
            ).text
        )[0]
        card_rating = ww.get_element_clickable(
            (By.XPATH, '//div[@class="_1mhd7uz"]//span[@role="img"]')
        ).text
        # Verify that the property displayed on the map matches some characteristics
        self.assertEqual(place_name, card_place_name)
        self.assertEqual(price_per_night, card_price_per_night)
        self.assertEqual(rating, card_rating)

        ##########
        # Step 7 #
        ##########
        ww.get_element_clickable((By.CSS_SELECTOR, 'button[aria-label=Close]')).click()
        ww.get_element_clickable((By.XPATH, '//span[text()="Filters"]')).click()
        ww.get_element_clickable((By.CSS_SELECTOR, 'label[for*=Entire_home] > div')).click()
        ww.get_element_clickable((By.CSS_SELECTOR, 'label[for*=Private_room] > div')).click()

        ##########
        # Step 8 #
        ##########
        try:
            ww.get_element_clickable((By.CSS_SELECTOR, 'label[for*=languages-8] > div'), timeout=4).click()
        except TimeoutException:
            ww.get_element_clickable((By.CSS_SELECTOR, 'label[for*=languages-8] > div'), timeout=2).click()
        ww.get_element_clickable((By.XPATH, '//a[contains(text(), "Show ")]')).click()

        # Check number of filters applied
        self.assertTrue(
            '3 filters applied' in ww.get_element_located(
                (By.XPATH, '//span[text()="Filters"]/../span[2]')
            ).text
        )

        nr_of_homes = int(ww.get_element_clickable(
            (By.XPATH, '//span[contains(text(), " homes")]')
        ).text.split()[0])

        nr_of_homes_shown = 0
        next_page_btn = ww.get_element_clickable((By.CSS_SELECTOR, 'a[aria-label="Next"]'))
        while True:
            nr_of_homes_shown += len(
                ww.get_all_elements_visible(
                    (By.CSS_SELECTOR, '[data-test-class=ExploreSectionWrapper] > div > div > div > div > div > div')
                )
            )
            next_page_btn.click()
            try:
                next_page_btn = ww.get_element_clickable((By.CSS_SELECTOR, 'a[aria-label="Next"]'), timeout=5)
            except TimeoutException:
                break

        # Check that the number of the homes shown is equal to the sum of every home on each page
        self.assertEqual(nr_of_homes, nr_of_homes_shown)
