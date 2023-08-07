import uuid
import os
from dotenv import load_dotenv
from selenium import webdriver
import pygsheets
from scraper.test_suite import TestSuite
from scraper.element import Element
from scraper.account import Account

load_dotenv()

# Read from Google sheet
gc = pygsheets.authorize(service_file = os.getenv("GOOGLE_SHEET_API_KEY_FILE"))

sht = gc.open_by_url(os.getenv("TEST_PLAN"))
wks_list = sht.worksheets()

target = {"uuid":"", "host":"", "case":"", "auth":"", "snapshot":"", "steps":[], "RWD":""}

## 環境變數
# UUID
target["uuid"] = uuid.uuid1()

# host
wks = sht[0]
host = wks.cell("A2")
target["host"] = host.value

# case
cases = wks.cell("B2")
target["case"] = cases.value

# auth
auth = wks.cell("C2")
target["auth"] = auth.value

# snapshot
snapshot = wks.cell("D2")
target["snapshot"] = snapshot.value

# RWD
rwd = wks.cell("E2")
target["RWD"] = rwd.value

# plan
wks = sht[1]
index_column = 0
list_row_data = wks.get_row(1)
for obj in list_row_data:
    index_column += 1
    if obj == target["case"]:
        plan = obj
        break

list_col = wks.get_col(index_column)

for obj in list_col[1:]:
    if (obj != ""):
        target["steps"].append(obj)

## Webdriver
options = webdriver.ChromeOptions()
options.add_argument("incognito")
options.add_argument("headless")

driver = webdriver.Chrome(options = options)
driver.maximize_window()

# create TestSuite object
test = TestSuite(driver,target["host"], target["case"], {
    "auth": target["auth"],
    "snapshot": target["snapshot"],
    "RWD": target["RWD"]
})

if(bool(test.options["auth"])):
    account = Account(test_suite=test,
                      login_id=Element('id', 'email', os.getenv("TESTER_EMAIL")),
                      password=Element('id', 'password', os.getenv("TESTER_PWD")))
    account.go_submit_form_with_account("/tplanet_signin.html",
                                        form_e=Element('tag_name', 'form'))

## Plan
for step in target["steps"]:
    test.jump_to_page(step)

    # Snapshot
    if (bool(test.options["snapshot"])):
        # Scroll
        test.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 擷取完整網頁截圖
        os.makedirs("output/", exist_ok=True)
        test.save_screenshot(f'output/{str(target["uuid"])}_{test.suite_name}_{step.replace("/","")}.png')

## TODO Report

## TODO: Notify

driver.quit()