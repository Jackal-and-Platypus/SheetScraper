import os
from dotenv import load_dotenv
from selenium import webdriver
from scraper.test_suite import TestSuite
from scraper.gsheet_manager import GsheetManager

load_dotenv()


def start_suite_test(suite: TestSuite, sheet_manager: GsheetManager):
    # auth
    if suite.options['auth']:
        # get auth by host
        sheet_manager.set_sheet_name('auth')
        sheet_manager.open_worksheet()
        auth_steps = sheet_manager.search_by_step_name(suite.host)
        suite.start_auth(auth_steps['steps'])
        suite.jump_to_page(suite.host)

    # get data from suite tab
    sheet_manager.set_sheet_name(suite.suite_name)
    sheet_manager.open_worksheet()
    cases = sheet_manager.get_steps()
    for case in cases:
        suite.start_case(case)
        sheet_manager.update_step_result_to_col(suite.report[-1], 6)

    # Report
    for i in range(len(suite.report)):
        success_steps = [step['result'] for step in suite.report[i]['report']]
        suite.report[i]['result'] = suite.get_result_from_list(success_steps)

    sheet_manager.update_case_result_to_col(suite.report, 6)


def main():
    # init
    os.makedirs("output/", exist_ok=True)
    sheet_url = os.getenv('TEST_PLAN')
    api_key_path = os.getenv('GOOGLE_SHEET_API_KEY_FILE')

    # Read from Google sheet
    sheet_manager = GsheetManager(api_key_path, sheet_url)
    sheet_manager.set_sheet_name('plan')
    sheet_manager.open_worksheet()
    plans = sheet_manager.get_plan()

    # Webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("incognito")
    options.add_argument("headless")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    for i in range(len(plans)):
        suite = TestSuite(driver, plans[i]["host"], plans[i]["suite"], {
            "auth": bool(plans[i]["auth"] == 'TRUE'),
            "snapshot": bool(plans[i]["snapshot"] == 'TRUE')
        })

        start_suite_test(suite, sheet_manager)
        suite_sheet = sheet_manager.open_worksheet()
        results = suite_sheet.get_col(6)
        plans[i]['name'] = plans[i]['suite']
        plans[i]['result'] = suite.get_result_from_list(results)
        sheet_manager.set_sheet_name('plan')
        sheet_manager.update_suite_result_to_col([plans[i]], 1)

    driver.quit()


if __name__ == "__main__":
    main()
