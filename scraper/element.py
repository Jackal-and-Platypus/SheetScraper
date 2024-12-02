from enum import Enum
from typing import Union
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from scraper.error_handler import ElementNotFoundError
from scraper.get_by import LocatorStrategyFactory


class ElementWaitType(Enum):
    CLICKABLE = "clickable"
    VISIBLE = "visible"


class Element:
    def __init__(
        self, by_method: str, by_value: str, value: Union[str, int, bool, float] = ""
    ):
        """
        初始化元素定位和操作資訊。

        Args:
            by_method: 定位方法（如 "id", "xpath" 等）
            by_value: 定位值
            value: 要操作的值（如要輸入的文字）

        Raises:
            ValueError: 當定位方法不支援時
        """
        # 檢查並保存定位方法
        self.locator = (LocatorStrategyFactory.get_by(by_method), by_value)
        self.value = value

    def find_element(
        self, driver: WebDriver, wait_type: ElementWaitType = ElementWaitType.CLICKABLE
    ) -> WebElement:
        """
        根據指定的等待條件找尋元素。

        這個方法整合了元素查找的邏輯，根據不同的等待類型使用對應的等待條件。
        如果找不到元素或發生其他錯誤，會拋出適當的例外。

        Args:
            driver: WebDriver 實例
            wait_type: 要使用的等待類型（可點擊或可見）

        Returns:
            找到的網頁元素

        Raises:
            ElementNotFoundError: 當元素在指定時間內找不到時
            TestConfigurationError: 當定位方法設定錯誤時
        """
        wait = WebDriverWait(driver, 30)  # 可以考慮將等待時間設為可配置參數

        # 根據等待類型選擇對應的等待條件
        wait_conditions = {
            ElementWaitType.CLICKABLE: EC.element_to_be_clickable,
            ElementWaitType.VISIBLE: EC.visibility_of_element_located,
        }

        wait_condition = wait_conditions[wait_type]

        try:
            return wait.until(wait_condition(self.locator))
        except TimeoutException:
            error_message = "無法找到元素"
            error_details = (
                f"等待類型: {wait_type.value}, "
                f"定位方法: {self.by_method}, "
                f"定位值: {self.by_value}"
            )
            raise ElementNotFoundError(error_message, error_details)

    @property
    def by_method(self):
        return self.locator[0]

    @property
    def by_value(self):
        return self.locator[1]

    @classmethod
    def from_dict(cls, input_dict):
        return cls(input_dict["by_method"], input_dict["by_value"], input_dict["value"])
