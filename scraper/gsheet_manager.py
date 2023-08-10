import os
import pygsheets
from dotenv import load_dotenv

load_dotenv()

class SheetScraper:
    def __init__(self, credentials_path, spreadsheet_url, sheet_name):
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.sheet_name = sheet_name
        self.client = self.authenticate()

    def authenticate(self):
        return pygsheets.authorize(service_file = self.credentials_path)

    def get_steps(self):
        spreadsheet = self.client.open_by_url(self.spreadsheet_url)
        sheet = spreadsheet.worksheet_by_title(self.sheet_name)
        data = sheet.get_all_records()

        all_steps = []
        current_step = None

        for row in data:
            step_number = row.get('step')
            if step_number == "#":
                if current_step is not None:
                    all_steps.append(current_step)
                current_step = {
                    "name": row.get('action_type'),
                    "steps": []
                }
            else:
                step_info = {
                    "action_type": row.get('action_type'),
                    "by_method": row.get('by_method'),
                    "by_value": row.get('by_value'),
                    "value": row.get('value')
                }
                if current_step is not None:
                    current_step["steps"].append(step_info)

        if current_step is not None:
            all_steps.append(current_step)

        return all_steps

    def get_plan(self):
        sheet = self.client.open_by_url(self.spreadsheet_url)
        worksheet = sheet.worksheet_by_title(self.sheet_name)
        records = worksheet.get_all_records()

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


if __name__ == "__main__":
    credentials_path = os.getenv("GOOGLE_SHEET_API_KEY_FILE")
    spreadsheet_url = os.getenv("TEST_PLAN")
    sheet_name = "suite_members"
    plan_sheet_name = "plan"

    scraper = SheetScraper(credentials_path, spreadsheet_url, sheet_name)
    steps = scraper.get_steps()


    scraper = SheetScraper(credentials_path, spreadsheet_url, plan_sheet_name)
    plan = scraper.get_plan()

