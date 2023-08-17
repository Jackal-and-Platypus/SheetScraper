import os
import pygsheets
from dotenv import load_dotenv

load_dotenv()


class GsheetManager:
    def __init__(self, credentials_path, spreadsheet_url):
        self.sheet_name = ""
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.client = self.authenticate()

    def authenticate(self):
        return pygsheets.authorize(service_file=self.credentials_path)

    def open_worksheet(self):
        spreadsheet = self.client.open_by_url(self.spreadsheet_url)
        sheet = spreadsheet.worksheet_by_title(self.sheet_name)
        return sheet

    def set_sheet_name(self, sheet_name):
        self.sheet_name = sheet_name

    def get_records(self):
        sheet = self.open_worksheet()
        records = sheet.get_all_records()
        return records

    def get_values(self):
        sheet = self.open_worksheet()
        values = sheet.get_all_values()
        return values

    def get_steps(self):
        records = self.get_records()

        all_steps = []
        current_step = None

        for row in records:
            step_number = row.get('step')
            if step_number == "#":
                if current_step is not None:
                    all_steps.append(current_step)
                current_step = {
                    "name": row.get('action_type'),
                    "steps": []
                }
            elif current_step is not None and row.get('action_type') != "":
                step_info = {
                    "action_type": row.get('action_type'),
                    "by_method": row.get('by_method') or "None",
                    "by_value": row.get('by_value') or "None",
                    "value": row.get('value') or "None"
                }
                current_step["steps"].append(step_info)

        if current_step is not None:
            all_steps.append(current_step)

        return all_steps

    def get_plan(self):
        records = self.get_records()

        test_plan = []
        for record in records:
            plan_entry = {
                "host": record["host"],
                "suite": record["suite"],
                "auth": record["auth"],
                "snapshot": record["snapshot"]
            }
            test_plan.append(plan_entry)

        return test_plan

    def update_case_result_to_col(self, case_reports, col):
        sheet = self.open_worksheet()
        for report in case_reports:
            row = self.search_row_by_name(report["name"])
            print(sheet.get_value((row, col)))
            sheet.update_value((row, col), report["result"])

    def search_by_step_name(self, name):
        steps = self.get_steps()

        case = None
        for step in steps:
            if step["name"] == name:
                case = step
                break

        return case

    def search_by_plan_host(self, host):
        steps = self.get_plan()

        result = []
        for step in steps:
            if step["host"] == host:
                result.append(step)

        return result

    def search_row_by_name(self, name):
        values = self.get_values()
        row = 0

        for value in values:
            if value[0] == '#' and value[1] == name:
                break
            row += 1

        return row + 1


if __name__ == "__main__":
    credentials_path = os.getenv("GOOGLE_SHEET_API_KEY_FILE")
    spreadsheet_url = os.getenv("TEST_PLAN")
    scraper = GsheetManager(credentials_path, spreadsheet_url)

    sheet_name = "suite_members"
    scraper.set_sheet_name(sheet_name)
    steps = scraper.get_steps()

    plan_sheet_name = "plan"
    scraper.set_sheet_name(plan_sheet_name)
    plan = scraper.get_plan()

    name_to_search = "註冊"
    scraper.set_sheet_name(sheet_name)
    search_case = scraper.search_by_step_name(name_to_search)

    host_to_search = "https://tplanet.townway.com.tw/"
    scraper.set_sheet_name(plan_sheet_name)
    search_result = scraper.search_by_plan_host(host_to_search)

    scraper.set_sheet_name('test_case')
    record = scraper.get_records()
    row = scraper.search_row_by_name('auth_screenshot')

    report = [{'name': 'index_RWD', 'result': 'success',
               'report': [{'step': 3, 'action': 'check_css', 'value': '{"display":"none"}', 'result': 'success'},
                          {'step': 5, 'action': 'check_css', 'value': '{"display":"block"}', 'result': 'success'}]},
              {'name': 'auth_screenshot', 'result': 'success', 'report': [
                  {'step': 1, 'action': 'check_link', 'value': '/backend/cms_project_detail.html?uuid=48821098',
                   'result': 'success'},
                  {'step': 2, 'action': 'check_link', 'value': '/backend/admin_agent_dashboard.html',
                   'result': 'success'}]}]
    # sheet = scraper.open_worksheet()
    # print(sheet.get_all_values())
    # print(sheet.get_all_records())

    scraper.update_case_result_to_col(report, 6)

    pass
