from selenium.webdriver.chrome.webdriver import WebDriver

from scraper.commands.base import TestCommand
from scraper.commands.check import CheckCssCommand, CheckLinkCommand
from scraper.commands.element_interaction import ClickCommand, HoverCommand, InputCommand, SubmitCommand
from scraper.commands.page import PageCommand
from scraper.commands.wait import WaitForInvisibleCommand, WaitForVisibleCommand
from scraper.commands.window import WebWidthCommand

class TestCommandFactory:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._commands = {
            "page": PageCommand(driver),
            "click": ClickCommand(driver),
            "input": InputCommand(driver),
            "submit": SubmitCommand(driver),
            "hover": HoverCommand(driver),
            "visible": WaitForVisibleCommand(driver),
            "invisible": WaitForInvisibleCommand(driver),
            "web_width": WebWidthCommand(driver),
            "check_css": CheckCssCommand(driver),
            "check_link": CheckLinkCommand(driver),
            # 可以輕鬆添加新的命令類型
        }

    def get_command(self, action_type: str) -> TestCommand:
        command = self._commands.get(action_type)
        if not command:
            raise ValueError(f"Unknown action type: {action_type}")
        return command
