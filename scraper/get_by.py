from enum import Enum
from selenium.webdriver.common.by import By
from typing import Dict


class LocatorStrategy(Enum):
    """
    定義所有支援的定位策略。
    使用 Enum 可以讓我們更容易管理所有可用的定位方法，
    並且提供了型別安全性。
    """

    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"
    NAME = "name"
    TAG_NAME = "tag_name"
    CLASS_NAME = "class_name"
    CSS = "css"


class LocatorStrategyFactory:
    """
    負責將定位策略字串轉換為 Selenium 的 By 類型。
    使用工廠模式可以集中管理所有的定位策略轉換邏輯。
    """

    _strategy_map: Dict[str, By] = {
        LocatorStrategy.ID.value: By.ID,
        LocatorStrategy.XPATH.value: By.XPATH,
        LocatorStrategy.LINK_TEXT.value: By.LINK_TEXT,
        LocatorStrategy.PARTIAL_LINK_TEXT.value: By.PARTIAL_LINK_TEXT,
        LocatorStrategy.NAME.value: By.NAME,
        LocatorStrategy.TAG_NAME.value: By.TAG_NAME,
        LocatorStrategy.CLASS_NAME.value: By.CLASS_NAME,
        LocatorStrategy.CSS.value: By.CSS_SELECTOR,
    }

    @classmethod
    def get_by(cls, by_method: str) -> By:
        """
        將字串形式的定位方法轉換為 Selenium 的 By 類型。

        Args:
            by_method: 定位方法的字串表示

        Returns:
            對應的 Selenium By 類型

        Raises:
            ValueError: 當提供的定位方法不支援時
        """
        strategy = cls._strategy_map.get(by_method.lower())
        if strategy is None:
            supported_methods = ", ".join(cls._strategy_map.keys())
            raise ValueError(
                f"不支援的定位方法: '{by_method}'. "
                f"支援的方法有: {supported_methods}"
            )
        return strategy

    @classmethod
    def is_valid_strategy(cls, by_method: str) -> bool:
        """
        檢查是否為支援的定位方法。

        Args:
            by_method: 要檢查的定位方法

        Returns:
            是否支援該定位方法
        """
        return by_method.lower() in cls._strategy_map
