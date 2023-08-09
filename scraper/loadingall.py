import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

class SheetScraper:
    def __init__(self, credentials_path, spreadsheet_key, sheet_name):
        self.credentials_path = credentials_path
        self.spreadsheet_key = spreadsheet_key
        self.sheet_name = sheet_name

    def get_steps(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        client = gspread.authorize(credentials)

        sheet = client.open_by_key(self.spreadsheet_key).worksheet(self.sheet_name)
        data = sheet.get_all_records()

        all_steps = []
        current_step = None

        for row in data:
            if row.get('step') == '#':        
                if current_step is not None:
                    all_steps.append(current_step)
                current_step = {
                    "name": row.get('value'),
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


if __name__ == "__main__":
    credentials_path = "D:/teak-photon-389315-7e5006f52334.json"
    spreadsheet_key = "1_8bRVul7NE_u8gjVIVML8_5qO1LWEuIJX4s35yCLiEQ"
    sheet_name = "suite_members"

    scraper = SheetScraper(credentials_path, spreadsheet_key, sheet_name)
    steps = scraper.get_steps()

    print(json.dumps(steps, ensure_ascii=False, indent=4))