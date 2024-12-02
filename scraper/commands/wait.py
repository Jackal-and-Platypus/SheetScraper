from abc import abstractmethod
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.commands.element_interaction import ElementInteractionCommand
from scraper.element import Element, ElementWaitType
from scraper.error_handler import ElementNotFoundError, TestConfigurationError


class WaitCommand(ElementInteractionCommand):
    """
    處理各種等待條件的命令類別。

    這個類別透過 Element 類別提供的功能來處理元素等待的邏輯，
    不同的等待類型（可見/不可見）透過不同的命令類別來實現。
    """

    def __init__(self, driver: WebDriver, timeout: int = 30):
        super().__init__(driver)
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    def _execute_command(self, step: dict) -> str:
        try:
            element = Element.from_dict(step)
            self.wait_for_condition(element)
            return "success"
        except TestConfigurationError as e:
            print(f"配置錯誤: {e.message}")
            if e.details:
                print(f"詳細資訊: {e.details}")
            return "failure"
        except ElementNotFoundError as e:
            print(f"元素未找到: {e.message}")
            if e.details:
                print(f"詳細資訊: {e.details}")
            return "failure"
        except Exception as e:
            print(f"未預期的錯誤: {str(e)}")
            return "failure"

    def wait_for_condition(self, element: Element):
        """
        子類別需要實作這個方法來定義具體的等待邏輯。
        """
        raise NotImplementedError


class WaitForVisibleCommand(WaitCommand):
    """
    等待元素變為可見的命令。
    使用 Element 類別的 find_element 方法，指定等待類型為 VISIBLE。
    """

    def wait_for_condition(self, element: Element):
        element.find_element(self.driver, ElementWaitType.VISIBLE)


class WaitForInvisibleCommand(WaitCommand):
    """
    等待元素變為不可見的命令。
    這個情況比較特殊，因為我們要等待元素不可見，
    所以需要直接使用 WebDriverWait。
    """

    def wait_for_condition(self, element: Element):
        self._wait.until(EC.invisibility_of_element_located(element.locator))
