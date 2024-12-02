from scraper.commands.base import TestCommand
from scraper.error_handler import ElementNotFoundError, TestConfigurationError
from scraper.element import Element
import json
import requests
from urllib.parse import urljoin


class CheckCommand(TestCommand):
    """檢查命令的基礎類別"""

    def _execute_command(self, step: dict) -> str:
        try:
            element = Element.from_dict(step)
            return self.perform_check(element)
        except (ElementNotFoundError, TestConfigurationError) as e:
            print(f"檢查失敗: {e.message}")
            if e.details:
                print(f"詳細資訊: {e.details}")
            return "failure"
        except Exception as e:
            print(f"未預期的錯誤: {str(e)}")
            return "failure"

    def perform_check(self, element: Element) -> str:
        raise NotImplementedError


class CheckCssCommand(CheckCommand):
    """檢查 CSS 屬性的命令"""

    def perform_check(self, element: Element) -> str:
        try:
            value = json.loads(element.value)
            web_element = element.find_element(self.driver)

            for css_property, expected_value in value.items():
                actual_value = web_element.value_of_css_property(css_property)
                if actual_value != expected_value:
                    return "failure"
            return "success"
        except json.JSONDecodeError:
            raise TestConfigurationError("CSS 檢查值必須是有效的 JSON 格式")


class CheckLinkCommand(CheckCommand):
    """檢查連結的命令"""

    def perform_check(self, element: Element) -> str:
        target_url = urljoin(self.host, element.value)

        # 如果有指定元素，先檢查當前 URL
        if element.by_method != "None":
            current_url = self.driver.current_url
            if current_url != target_url:
                return "failure"

        try:
            response = requests.get(target_url)
            return "success" if response.status_code == 200 else "failure"
        except requests.RequestException as e:
            print(f"請求失敗: {str(e)}")
            return "failure"
