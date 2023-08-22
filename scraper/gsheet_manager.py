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

    def update_result_to_col(self, reports, search_col_name, col):
        sheet = self.open_worksheet()
        for report in reports:
            search_col = self.search_col_by_index(search_col_name)
            row = self.search_row_by_col_and_value(search_col, report["name"])
            sheet.update_value((row, col), report["result"])

    def update_step_result_to_col(self, case_reports, col):
        sheet = self.open_worksheet()
        for step in case_reports['report']:
            print('step: ', step)
            if 'result' in step.keys() is False:
                continue
            search_col = self.search_col_by_index('action_type')
            row = self.search_row_by_col_and_value(search_col, case_reports["name"]) + step['step']
            sheet.update_value((row, col), step["result"])

    def update_case_result_to_col(self, case_reports, col):
        self.update_result_to_col(case_reports, 'action_type', col)

    def update_suite_result_to_col(self, suite_reports, col):
        self.update_result_to_col(suite_reports, 'suite', col)

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

    def search_row_by_col_and_value(self, col, value):
        cell_values = self.get_values()
        row = 0

        for cell_value in cell_values:
            if cell_value[col - 1] == value:
                break
            row += 1

        return row + 1

    def search_col_by_index(self, index):
        sheet = self.open_worksheet()
        row = sheet.get_row(1)

        return row.index(index) + 1
