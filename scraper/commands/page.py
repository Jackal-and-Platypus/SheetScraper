from urllib.parse import urljoin
from scraper.commands.base import TestCommand


class PageCommand(TestCommand):
    def _execute_command(self, step: dict) -> str:
        try:
            self.driver.get(urljoin(self.host, step["value"]))
            return "success"
        except Exception as e:
            print(f"Failed to navigate: {e}")
            return "failure"
