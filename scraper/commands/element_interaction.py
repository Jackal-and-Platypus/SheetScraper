from scraper.commands.base import TestCommand
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from scraper.element import Element, ElementWaitType
from scraper.error_handler import ElementNotFoundError, TestConfigurationError
from scraper.get_by import LocatorStrategyFactory


class ElementInteractionCommand(TestCommand):
    """
    提供基礎的元素互動功能的抽象類別。
    這個類別包含了所有與元素互動相關的共用方法，讓子類別可以重複使用這些功能。
    """

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 30)  # 將等待時間設為可配置的參數會更好

    def _execute_command(self, step: dict) -> str:
        try:
            element_obj = Element.from_dict(step)
            # 根據命令的需求選擇適當的等待類型
            element = element_obj.find_element(
                self.driver, ElementWaitType.CLICKABLE  # 或 ElementWaitType.VISIBLE
            )
            # 執行元素操作
            self.perform_action(element, element_obj.value)
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

    def perform_action(self, element: WebElement, value: str):
        """
        各個子類別實作此方法來定義具體的元素操作
        """
        raise NotImplementedError

    def find_clickable_element(self, step: dict):
        """
        尋找可點擊的元素。這個方法被多個命令共用，因此放在父類別中。

        Args:
            step: 包含元素定位資訊的字典

        Returns:
            WebElement: 找到的網頁元素

        Raises:
            TimeoutException: 當元素在指定時間內無法點擊時
        """
        try:
            element = Element.from_dict(step)
            return self.wait.until(EC.element_to_be_clickable(element.locator))
        except ValueError as e:
            raise TestConfigurationError(f"定位方法設定錯誤: {e}")
        except TimeoutException:
            raise ElementNotFoundError(f"無法找到可點擊的元素: {element.by_value}")

    def find_visible_element(self, step: dict):
        """
        尋找可見的元素。某些操作可能只需要元素可見而不一定要可點擊。
        """
        by_method = LocatorStrategyFactory.get_by(step["by_method"])
        locator = (by_method, step["by_value"])
        return self.wait.until(EC.visibility_of_element_located(locator))

    def handle_error(self, error: Exception, step: dict):
        """
        統一的錯誤處理邏輯。
        """
        print(f"Failed to perform {step['action_type']}: {error}")
        # 可以添加更多的錯誤處理邏輯，如記錄日誌等


# 繼承基礎類別來實現具體的命令
class ClickCommand(ElementInteractionCommand):
    """
    處理點擊操作的命令類別。
    """
    def perform_action(self, element: WebElement, value: str):
        ActionChains(self.driver).click(element).perform()


class InputCommand(ElementInteractionCommand):
    """
    處理輸入操作的命令類別。
    重用了父類別的 find_clickable_element 方法。
    """
    def perform_action(self, element: WebElement, value: str):
        element.clear()
        element.send_keys(value)


class SubmitCommand(ElementInteractionCommand):
    """
    處理表單提交操作的命令類別。
    重用了父類別的 find_clickable_element 方法。
    """
    def perform_action(self, element: WebElement, value: str):
        element.submit()


class HoverCommand(ElementInteractionCommand):
    """
    處理滑鼠懸停操作的命令類別。
    這裡使用 find_visible_element 而不是 find_clickable_element，
    因為懸停操作只需要元素可見即可。
    """

    def _execute_command(self, step: dict) -> str:
        # 覆寫 _execute_command 方法來使用 VISIBLE 等待類型
        try:
            element_obj = Element.from_dict(step)
            element = element_obj.find_element(
                self.driver,
                ElementWaitType.VISIBLE
            )
            ActionChains(self.driver).move_to_element(element).perform()
            return "success"
        except (TestConfigurationError, ElementNotFoundError) as e:
            print(f"{e.message} - {e.details}")
            return "failure"
        except Exception as e:
            print(f"未預期的錯誤: {str(e)}")
            return "failure"
