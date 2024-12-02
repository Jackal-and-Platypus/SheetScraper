import uuid
import json
from xmlrpc.client import Boolean
import requests
from time import sleep
from time import perf_counter
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from scraper.element import Element


def get_by(by_method: str):
    if by_method == "id":
        return By.ID
    elif by_method == "xpath":
        return By.XPATH
    elif by_method == "link_text":
        return By.LINK_TEXT
    elif by_method == "partial_link_text":
        return By.PARTIAL_LINK_TEXT
    elif by_method == "name":
        return By.NAME
    elif by_method == "tag_name":
        return By.TAG_NAME
    elif by_method == "class_name":
        return By.CLASS_NAME
    elif by_method == "css":
        return By.CSS_SELECTOR

def add_step_report(index, step, result):
    step_report = {
        "step": index,
        "row": step["row"],
        "action": step["action_type"],
        "value": step["value"],
        "result": result,
    }
    print("    => " + result)

    return step_report

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
        for step in case["steps"]:
            step_print = str(i) + ": " + step["action_type"]
            if step["by_method"] != "None":
                step_print += f"({step['by_method']}|{step['by_value']}) "
            step_print += f" -> {step['value']}"
            print(step_print)

            if step["action_type"][:6] == "check_":
                result = self.check_test(step)
                case_report["report"].append(add_step_report(i, step, result))
                print("    => " + result)

            else:
                result = self.start_step(step)
                if result is not None:
                    case_report["report"].append(add_step_report(i, step, result))

            if self.options["snapshot"]:
                file_name = f'{self.uuid_id}_{self.suite_name}_{case["name"]}_{i}'
                self.save_screenshot(f"output/{file_name}.png")
            i += 1

        self.report.append(case_report)

    def start_auth(self, steps: list[dict]):
        print("Starting auth")
        for step in steps:
            print(step)
            self.start_step(step)

    def start_step(self, step: dict):
        sleep(0.5)
        start_time = perf_counter()
        if "by_method" in step and step["by_method"] is not None:
            element = Element.from_dict(step)
        try:
            if step["action_type"] == "page":
                self.jump_to_page(step["value"])
            elif step["action_type"] == "click":
                self.click_element(element)
            elif step["action_type"] == "input":
                self.input_field(element)
            elif step["action_type"] == "web_width":
                self.set_web_width(int(step["value"]))
            elif step["action_type"] == "submit":
                self.submit(element)
            elif step["action_type"] == "visible":
                self.wait_until(
                    EC.visibility_of_element_located(self.get_locator(element))
                )
            elif step["action_type"] == "invisible":
                self.wait_until_not(
                    EC.visibility_of_element_located(self.get_locator(element))
                )
            elif step["action_type"] == "hover":
                self.hover_element(element)

        except Exception as e:
            print(e)
            return "failure"
        end_time = perf_counter()
        print(f"duration: {end_time - start_time} seconds")
        sleep(0.5)

    def check_test(self, step: dict) -> str:
        element = Element.from_dict(step)

        try:
            if step["action_type"] == "check_css":
                if "failure" in self.check_css(element):
                    return "failure"
                else:
                    return "success"
            elif step["action_type"] == "check_link":
                if element.by_method == "None":
                    return self.check_link(element)
                else:
                    self.click_element(element)
                    return self.check_link(element)
        except Exception as e:
            print(e)
            return "except failure"

    def check_css(self, element: Element) -> str:
        value = json.loads(element.value)
        result = []

        for k, v in value.items():
            target = self.find_visible_element(element).value_of_css_property(k)
            if target == v:
                result.append("success")
            else:
                result.append("failure")

        return result

    def check_link(self, element: Element) -> str:
        target_url = urljoin(self.host, element.value)

        if element.by_method != "None":
            if self.driver.current_url != target_url:
                return "failure"

        if requests.get(target_url).status_code == 200:
            return "success"
        else:
            return "failure"

    def get_result_from_list(self, result_list: list) -> str:
        if "failure" in result_list or "except failure" in result_list:
            return "failure"
        return "success"

    def jump_to_page(self, url: str):
        self.driver.get(urljoin(self.host, url))

    def input_field(self, element: Element):
        self.find_clickable_element(element).send_keys(element.value)

    def submit(self, form_e: Element):
        self.find_clickable_element(form_e).submit()

    def click_element(self, element: Element):
        element = self.find_clickable_element(element)
        click = ActionChains(self.driver).click(element)
        click.perform()

    def wait_until(self, expect_condition_is: Boolean, timeout=30):
        WebDriverWait(self.driver, timeout).until(expect_condition_is)

    def wait_until_not(self, expect_condition_is: Boolean, timeout=30):
        WebDriverWait(self.driver, timeout).until_not(expect_condition_is)

    def hover_element(self, element: Element):
        element = self.find_visible_element(element)
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

    def find_visible_element(self, element: Element, timeout=30):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.get_locator(element))
        )

    def find_clickable_element(self, element: Element, timeout=30):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.get_locator(element))
        )

    def get_locator(self, element: Element) -> tuple:
        return (get_by(element.by_method), element.by_value)

    def set_web_width(self, width: int):
        original_size = self.driver.get_window_size()
        self.driver.set_window_size(width, original_size["height"])

    def save_screenshot(self, path: str):
        original_size = self.driver.get_window_size()
        required_width = self.driver.execute_script(
            "return document.body.parentNode.scrollWidth"
        )
        required_height = self.driver.execute_script(
            "return document.body.parentNode.scrollHeight"
        )
        self.driver.set_window_size(required_width, required_height)
        self.driver.find_element(By.TAG_NAME, "body").screenshot(
            path
        )  # avoids scrollbar
        self.driver.set_window_size(original_size["width"], original_size["height"])
