import uuid
import os
from dotenv import load_dotenv
import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pygsheets

load_dotenv()

def save_screenshot(driver, path):
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    driver.find_element(By.TAG_NAME, 'body').screenshot(path)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])

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
if not os.path.exists("output"):
    os.makedirs("output")


options = webdriver.ChromeOptions()
options.add_argument("incognito")
options.add_argument("--headless")

driver = webdriver.Chrome(options = options)
driver.maximize_window()

url_target = target["host"]
if(bool(target["auth"])):
  url_target = url_target + "/tplanet_signin.html"
  driver.get(url_target)
  driver.find_element(By.ID, value = "email").send_keys(os.getenv("TESTER_EMAIL"))
  driver.find_element(By.ID, value = "password").send_keys(os.getenv("TESTER_PWD"))
  driver.find_element(By.TAG_NAME, "form").submit()
  time.sleep(5)

## Plan
for step in target["steps"]:
    driver.get(target["host"] + step)
    time.sleep(5)

    # Snapshot
    if (bool(target["snapshot"])):
      # Scroll
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

      # 擷取完整網頁截圖
      save_screenshot(driver, "output/" + str(target["uuid"]) + ".png")

## TODO Report
# 將 target 字典的資料儲存為 CSV 檔案
output_file = "output/test_report.csv"

target["write_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 檢查 CSV 檔案是否存在
file_exists = os.path.exists(output_file)

# 檢查是否已經存在欄位名稱
field_names = list(target.keys())
fields_to_write = []

if file_exists:
    with open(output_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fields_to_write = [field for field in field_names if field not in reader.fieldnames]

# 加上 "write_time" 欄位到 fields_to_write
fields_to_write.append("write_time")

# 使用 csv 模組寫入 CSV 檔案
with open(output_file, "a", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=field_names)

    # 若 CSV 檔案不存在，寫入 CSV 標題列
    if not file_exists:
        writer.writeheader()

    # 寫入 target 字典的資料作為一行資料
    writer.writerow(target)

print(f"已將 target 資料附加到 {output_file} 檔案中。")

## TODO: Notify

driver.quit()