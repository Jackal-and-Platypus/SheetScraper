import os
import pygsheets
from dotenv import load_dotenv

load_dotenv()

class GsheetManager:
    def __init__(self, credentials_path, spreadsheet_url):
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.client = self.authenticate()

    def authenticate(self):
        return pygsheets.authorize(service_file = self.credentials_path)

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
                "snapshot": record["snapshot"],
                "restart": record["restart"]
            }
            test_plan.append(plan_entry)

        return test_plan

    def search_by_name(self, name):
        steps = self.get_steps()

        result = None
        for step in steps:
            if step["name"] == name:
                result = step
                break

        return result

def search_steps_by_name(credentials_path, spreadsheet_url, sheet_name, name):
    scraper = GsheetManager(credentials_path, spreadsheet_url)
    scraper.set_sheet_name(sheet_name)
    result = scraper.search_by_name(name)
    return result


if __name__ == "__main__":
    credentials_path = os.getenv("GOOGLE_SHEET_API_KEY_FILE")
    spreadsheet_url = os.getenv("TEST_PLAN")
    scraper = GsheetManager(credentials_path, spreadsheet_url)
    
    sheet_name = "suite_members"
    scraper.set_sheet_name(sheet_name)
    steps = scraper.get_steps()
    print("test_steps =")
    print(steps)


    plan_sheet_name = "plan"
    scraper.set_sheet_name(plan_sheet_name)
    plan = scraper.get_plan()
    print("test_plan =")
    print(plan)

    name_to_search = "刪除帳號"
    sheet_name = "suite_members"
    scraper.set_sheet_name(sheet_name)
    search_result = scraper.search_by_name(name_to_search)
    if search_result is None:
        print("No matching content found")
    else:
        print(search_result)
