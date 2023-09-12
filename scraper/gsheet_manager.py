import pygsheets


class GsheetManager:
    def __init__(self, credentials_path: str, spreadsheet_url: str):
        self.sheet_name = ""
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.client = self.authenticate()
        self.sheet = None

    def authenticate(self):
        return pygsheets.authorize(service_file=self.credentials_path)

    def open_worksheet(self, sheet_name: str):
        self.set_sheet_name(sheet_name)
        spreadsheet = self.client.open_by_url(self.spreadsheet_url)
        self.sheet = spreadsheet.worksheet_by_title(sheet_name)

    def set_sheet_name(self, sheet_name: str):
        self.sheet_name = sheet_name

    def get_records(self):
        records = self.sheet.get_all_records()
        return records

    def get_values(self):
        values = self.sheet.get_all_values()
        return values

    def get_steps(self):
        records = self.get_values()
        index_col_map = {}

        for i in range(len(records[0])):
            index_col_map[records[0][i]] = i

        all_steps = []
        current_step = None

        for row_index in range(1, len(records)):
            row = records[row_index]
            step_number = row[index_col_map['step']]
            if step_number == "":
                continue

            if step_number == "#":
                if current_step is not None:
                    all_steps.append(current_step)
                current_step = {
                    "name": row[index_col_map['action_type']],
                    "row": row_index + 1,
                    "steps": []
                }
            elif current_step is not None and row[index_col_map['action_type']] != "":
                step_info = {
                    "step_value": row[index_col_map['step']],
                    "row": row_index + 1,
                    "action_type": row[index_col_map['action_type']],
                    "by_method": row[index_col_map['by_method']] or "None",
                    "by_value": row[index_col_map['by_value']] or "None",
                    "value": row[index_col_map['value']] or "None"
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

    def update_result(self, report: dict, col: int):
        row = report["row"]
        self.sheet.update_value((row, col), report["result"])

    def search_by_step_name(self, name: str):
        steps = self.get_steps()

        case = None
        for step in steps:
            if step["name"] == name:
                case = step
                break

        return case

    def search_by_plan_host(self, host: str):
        steps = self.get_plan()

        result = []
        for step in steps:
            if step["host"] == host:
                result.append(step)

        return result
