from abc import ABC, abstractmethod
from time import perf_counter, sleep
from selenium.webdriver.chrome.webdriver import WebDriver


class TestCommand(ABC):
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def execute(self, step: dict) -> str:
        start_time = perf_counter()
        try:
            result = self._execute_command(step)
            end_time = perf_counter()
            print(f"duration: {end_time - start_time} seconds")
            sleep(0.5)

            return result

        except Exception as e:
            print(e)
            return "failure"

    @abstractmethod
    def _execute_command(self, step: dict) -> str:
        # 具體命令的實現邏輯
        pass
