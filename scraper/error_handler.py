class TestError(Exception):
    """
    測試相關錯誤的基礎類別。
    所有自訂的測試錯誤都應該繼承這個類別，這樣可以在需要時統一處理所有測試相關的錯誤。
    """

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


# 定義特定類型的錯誤
class TestConfigurationError(TestError):
    """
    當測試配置有誤時拋出的錯誤。
    例如：使用了不支援的元素定位方法。
    """

    pass


class ElementNotFoundError(TestError):
    """
    當無法在頁面上找到指定元素時拋出的錯誤。
    這與 Selenium 的 TimeoutException 不同，因為它提供了更具體的錯誤資訊。
    """

    pass

