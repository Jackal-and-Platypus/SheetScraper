import uuid
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from scraper.element import Element


def get_by(by_method):
    if by_method == 'id':
        return By.ID
    elif by_method == 'tag_name':
        return By.TAG_NAME


class TestSuite:
    def __init__(self, driver: WebDriver, host: str, suite_name: str, options: dict):
        self.driver = driver
        self.uuid_id = uuid.uuid1()
        self.host = host
        self.suite_name = suite_name
        self.options = options

    def jump_to_page(self, url: str):
        self.driver.get(self.host + url)
        sleep(5)

    def input_field(self, element: Element):
        self.driver.find_element(get_by(element.by_method),element.by_value).send_keys(element.value)

    def submit(self, form_e: Element):
        self.driver.find_element(get_by(form_e.by_method), form_e.by_value).submit()
        sleep(5)

    def go_submit_form_with_params(self, url: str, form_e: Element, params: list[Element]):
        self.jump_to_page(url)
        for i in params:
            self.input_field(i)
        self.submit(form_e)

    def click_button(self, element:Element):
        self.driver.find_element(get_by(element.by_method),element.by_value).click()

    def save_screenshot(self, path):
        original_size = self.driver.get_window_size()
        required_width = self.driver.execute_script('return document.body.parentNode.scrollWidth')
        required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
        self.driver.set_window_size(required_width, required_height)
        # self.driver.save_screenshot(path)  # has scrollbar
        self.driver.find_element(By.TAG_NAME, 'body').screenshot(path)  # avoids scrollbar
        self.driver.set_window_size(original_size['width'], original_size['height'])
