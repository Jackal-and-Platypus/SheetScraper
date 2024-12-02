import uuid
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from scraper.commands.index import TestCommandFactory


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
        self.command_factory = TestCommandFactory(driver)
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
        try:
            command = self.command_factory.get_command(step["action_type"])
            return command.execute(step)
        except Exception as e:
            print(e)
            return "failure"

    def get_result_from_list(self, result_list: list) -> str:
        if "failure" in result_list or "except failure" in result_list:
            return "failure"
        return "success"

    def jump_to_page(self, url: str):
        self.driver.get(urljoin(self.host, url))

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
