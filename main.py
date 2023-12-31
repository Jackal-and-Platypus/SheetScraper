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
        sheet_manager.open_worksheet('auth')
        auth_steps = sheet_manager.search_by_step_name(suite.host)
        suite.start_auth(auth_steps['steps'])

    if suite.host != '':
        suite.jump_to_page(suite.host)

    # get data from suite tab
    sheet_manager.open_worksheet(suite.suite_name)
    cases = sheet_manager.get_steps()
    # Test Case
    for case in cases:
        print('# ' + case['name'])
        suite.start_case(case)
        for step_report in suite.report[-1]['report']:
            sheet_manager.update_result(step_report, 6)

    # Report
    for i in range(len(suite.report)):
        step_results = [step['result'] for step in suite.report[i]['report']]
        suite.report[i]['result'] = suite.get_result_from_list(step_results)
        sheet_manager.update_result(suite.report[i], 6)


def main():
    # init
    print("<< Starting SheetScraper >>")
    os.makedirs("output/", exist_ok=True)
    sheet_url = os.getenv('TEST_PLAN')
    api_key_path = os.getenv('GOOGLE_SHEET_API_KEY_FILE')

    # Read from Google sheet
    print("Reading Google sheet...")
    sheet_manager = GsheetManager(api_key_path, sheet_url)
    sheet_manager.open_worksheet('plan')
    plans = sheet_manager.get_plan()

    # Webdriver
    print("Creating Webdriver...")
    options = webdriver.ChromeOptions()
    options.add_argument("incognito")
    options.add_argument("headless")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    # Test Suite
    for i in range(len(plans)):
        suite = TestSuite(driver, plans[i]["host"], plans[i]["suite"], {
            "auth": bool(plans[i]["auth"] == 'TRUE'),
            "snapshot": bool(plans[i]["snapshot"] == 'TRUE')
        })
        print("========================================")
        print("[ Test Suite: " + suite.suite_name + " ]")

        start_suite_test(suite, sheet_manager)
        sheet_manager.open_worksheet(suite.suite_name)
        results = sheet_manager.sheet.get_col(6)
        plans[i]['name'] = plans[i]['suite']
        plans[i]['row'] = i + 2
        plans[i]['result'] = suite.get_result_from_list(results)
        sheet_manager.open_worksheet('plan')
        sheet_manager.update_result(plans[i], 1)

    print("========================================")
    print("FINISHED!")
    driver.quit()


if __name__ == "__main__":
    main()
