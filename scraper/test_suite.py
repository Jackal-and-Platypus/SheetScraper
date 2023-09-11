import uuid
import json
import requests
from time import sleep
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from scraper.element import Element


def get_by(by_method: str):
    if by_method == 'id':
        return By.ID
    elif by_method == 'xpath':
        return By.XPATH
    elif by_method == 'link_text':
        return By.LINK_TEXT
    elif by_method == 'partial_link_text':
        return By.PARTIAL_LINK_TEXT
    elif by_method == 'name':
        return By.NAME
    elif by_method == 'tag_name':
        return By.TAG_NAME
    elif by_method == 'class_name':
        return By.CLASS_NAME
    elif by_method == 'css':
        return By.CSS_SELECTOR


class TestSuite:
    def __init__(self, driver: WebDriver, host: str, suite_name: str, options: dict):
        self.driver = driver
        self.uuid_id = uuid.uuid1()
        self.host = host
        self.suite_name = suite_name
        self.options = options
        self.report = []

    def start_case(self, case: dict):
        case_report = {"name": case["name"], "row": case["row"], "report": []}
        i = 1
        for step in case['steps']:
            if step['action_type'][:6] == 'check_':
                result = self.check_test(step)
                case_report['report'].append(
                    {'step': i, 'row': step['row'], 'action': step['action_type'], 'value': step['value'], 'result': result})

            else:
                self.start_step(step)

            if self.options['snapshot']:
                file_name = f'{self.uuid_id}_{self.suite_name}_{case["name"]}_{i}'
                self.save_screenshot(f'output/{file_name}.png')
            i += 1

        self.report.append(case_report)

    def start_auth(self, steps: list[dict]):
        for step in steps:
            self.start_step(step)

    def start_step(self, step: dict):
        if 'by_method' in step and step['by_method'] is not None:
            element = Element.from_dict(step)
        try:
            if step['action_type'] == 'page':
                self.jump_to_page(step['value'])
            elif step['action_type'] == 'click':
                self.click_element(element)
            elif step['action_type'] == 'input':
                self.input_field(element)
            elif step['action_type'] == 'web_width':
                self.set_web_width(int(step['value']))
            elif step['action_type'] == 'submit':
                self.submit(element)
        except Exception as e:
            print(e)

    def check_test(self, step: dict) -> str:
        element = Element.from_dict(step)

        try:
            if step['action_type'] == 'check_css':
                if 'failure' in self.check_css(element):
                    return 'failure'
                else:
                    return 'success'
            elif step['action_type'] == 'check_link':
                if element.by_method == 'None':
                    return self.check_link(element)
                else:
                    self.click_element(element)
                    return self.check_link(element)
        except Exception as e:
            print(e)
            return 'except failure'

    def check_css(self, element: Element) -> str:
        value = json.loads(element.value)
        result = []

        for k, v in value.items():
            target = self.find_element(element).value_of_css_property(k)
            if target == v:
                result.append('success')
            else:
                result.append('failure')

        return result

    def check_link(self, element: Element) -> str:
        target_url = urljoin(self.host, element.value)

        if element.by_method != 'None':
            if self.driver.current_url != target_url:
                return 'failure'

        if requests.get(target_url).status_code == 200:
            return 'success'
        else:
            return 'failure'

    def get_result_from_list(self, result_list: list) -> str:
        if 'failure' in result_list or 'except failure' in result_list:
            return 'failure'
        return 'success'

    def jump_to_page(self, url: str):
        self.driver.get(urljoin(self.host, url))
        sleep(5)

    def input_field(self, element: Element):
        self.find_element(element).send_keys(element.value)

    def submit(self, form_e: Element):
        self.find_element(form_e).submit()
        sleep(5)

    def click_element(self, element: Element):
        self.find_element(element).click()
        sleep(5)

    def find_element(self, element: Element) -> WebElement:
        return self.driver.find_element(get_by(element.by_method), element.by_value)

    def set_web_width(self, width: int):
        original_size = self.driver.get_window_size()
        self.driver.set_window_size(width, original_size['height'])

    def save_screenshot(self, path: str):
        original_size = self.driver.get_window_size()
        required_width = self.driver.execute_script('return document.body.parentNode.scrollWidth')
        required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
        self.driver.set_window_size(required_width, required_height)
        self.driver.find_element(By.TAG_NAME, 'body').screenshot(path)  # avoids scrollbar
        self.driver.set_window_size(original_size['width'], original_size['height'])
