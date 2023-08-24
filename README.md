
# SheetScraper
<div id="top"></div>
<div id="top">
<p>
  <a href="https://github.com/Jackal-and-Platypus/SheetScraper" target="_blank">
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000" />
  </a>
  <a href="https://github.com/Jackal-and-Platypus/SheetScraper/blob/main/LICENSE" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/github/license/Jackal-and-Platypus/SheetScraper.svg" />
  </a>
</p>
</div>
<!-- TABLE OF CONTENTS -->
<details>
  <summary>目錄 Table of Contents</summary>
  <ol>
    <li>
      <a href="#關於-about">關於 About</a>
      <ul>
        <li><a href="#特色-Feature">特色 Feature</a></li>
        <li><a href="#截圖-Screenshot">截圖 Screenshot</a></li>
        <li><a href="#建置環境-built-with">建置環境 Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#入門-getting-started">入門 Getting Started</a>
      <ul>
        <li><a href="#前置-prerequisites">前置 Prerequisites</a></li>
        <li><a href="#安裝-installation">安裝 Installation</a></li>
      </ul>
    </li>
    <li><a href="#使用方法-usage">使用方法 Usage</a></li>
    <li><a href="#版權聲明-license">版權聲明 License</a></li>
    <li><a href="#致謝-acknowledgments">致謝 Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## 關於 About

「SheetScraper」是一個開源專案，它利用 Google Sheets 作為測試計畫（test plan），使用 Python 來讀取該測試計畫。這個專案使用 Selenium 來執行網站爬蟲。這個專案的主要目標是提供一個簡單而強大的工具，讓開發人員能夠使用 Google Sheets 來編寫測試計畫，並使用 Python 和 Selenium 來執行網站爬蟲，從而自動化測試和數據收集的流程。

### 特色 Feature

#### 不需會程式也能簡單使用
- 使用 Google Sheet 規劃和寫入 Test Plan

#### 陸續追加的網站測試功能
- 像使用者一樣按照步驟執行
- 檢查頁面跳轉回應的 status code 是否正確
- 支援需要帳號密碼登入的頁面

#### 每一步動作都會自動截圖
- 勾選 snapshot 就會在每個步驟截圖儲存

<p align="right">(<a href="#top">back to top</a>)</p>

### 建置環境 Built With

- Python (v3.9.13 / v3.11.4)
- Selenium
- pygsheets (Google Sheets API)
- .env（環境變數設定檔案）

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## 入門 Getting Started
### 前置 Prerequisites
#### Python
建置 python 虛擬環境，可使用 venv 或 conda。
##### venv
1. 確保系統中已經安裝 Python，可以前往 [Python 官方網站](https://www.python.org/downloads/) 下載
2. 建立虛擬環境
```sh
python -m venv venv
```
3. 啟動虛擬環境
   Windows: `venv\Scripts\activate`  
   Linux/mac: `source venv/bin/activate`
##### conda
1. 如果您尚未安裝 Conda，請前往 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 [Anaconda](https://www.anaconda.com/products/distribution) 官方網站下載和安裝 Miniconda 或 Anaconda
2. 建立虛擬環境
```sh
conda create --name SheetScraper python=3.11
```
3. 啟動虛擬環境
Windows: `activate SheetScraper`  
Linux/mac: `source activate SheetScraper`
#### Google Sheets
- [SheetScraper範例檔案](https://docs.google.com/spreadsheets/d/1zApqpIVTjPxquOjgaAsloD7UOvbJFh9R0KOJja9DXAw/edit?usp=sharing)
- [SheetScraper空白檔](https://docs.google.com/spreadsheets/d/1sJArDVQRs206BWaUaaAlEyffMFvwyRonkjHyJhaEfCg/edit?usp=sharing)

1. 為 `SheetScraper空白檔` 建立副本，作為 test plan 的輸入介面
2. 為 GCP 的服務帳戶建立金鑰，並儲存 JSON 檔
3. 將該服務帳戶加入 test plan 試算表的使用者，並允許編輯
 

### 安裝 Installation

1. 在要安裝的位置開啟終端機(terminal) clone 專案檔案
   ```sh
   git clone https://github.com/Jackal-and-Platypus/SheetScraper.git
   ```

2. 進入專案資料夾
   ```sh
   cd SheetScraper
   ```

3. 安裝所需套件
   ```sh
   pip install -r requirements.txt
   ```
   或
   ```sh
   conda install -r requirements.txt
   ```

4. 於 `/SheetScraper` 建立 `.env` 檔案，可複製 `.env.example` 加以修改，或是參考以下內容設定：
   ```
   GOOGLE_SHEET_API_KEY_FILE=API_KEY_PATH  
   TEST_PLAN=URL
   ```
`GOOGLE_SHEET_API_KEY_FILE`：先前下載的金鑰憑證路徑
`TEST_PLAN`：test plan 試算表連結

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE -->
## 使用方法 Usage
### 編寫 Test Plan
![plan](https://raw.githubusercontent.com/Jackal-and-Platypus/SheetScraper/main/images/plan.png)
分頁名稱必須為 `plan`
- `result`: 測試完成後會顯示 succes 或 failure
- `host`: 想要測試的網域，在跨多網域的情況下可以留空
- `suite`: Test Suite 的名稱，測試工具會依照這裡填寫的內容搜尋指定名稱的工作表分頁
- `auth`: 勾選後，在進行這項 Test Suite 前會事先進行認證（登入等）
- `snapshot`: 勾選後，進行這項 Test Suite 時，在每個 step 都會進行截圖

### Test Suite 分頁
分頁的名稱請依照 plan 分頁的 `suite`填寫
#### 步驟設定
![member](https://raw.githubusercontent.com/Jackal-and-Platypus/SheetScraper/main/images/members.png)
![css](https://raw.githubusercontent.com/Jackal-and-Platypus/SheetScraper/main/images/css_step.png)
- `#`: 定位每一個項目的首行，切勿刪除
- `#` 的右邊那格: Test Case 的名稱，不可重複
- `step`: 步驟順序
- `action_type`: 該步驟要做的事，搭配 `by_method` 、 `by_value` 和 `value` 填寫
	  - page: 前往指定頁面，不需填寫 `by_method` 與 `by_value`
	    `value`: 填寫指定連結，最終連結的網址會是 Test Plan 的 `host` + `value`
	  - click: 點擊指定元素
	  - input: 在指定的元素中填入 `value`
	  - web_width: 將瀏覽器頁面的寬度設定為 `value`，單位為像素(px)
	  - check_link: 確認指定連結的 status code 為 200，填寫 `by_method` 與 `by_value` 的情況下，會先點擊指定元素再確認跳轉後的頁面是否正常
	  - check_css: 確認指定元素的 css 屬性是否與 `value` 內容一致
	    `value`: 使用 JSON 的格式填寫要檢查的屬性和希望一致的值
	  - submit: 觸發指定的 form 元素的送出事件
- `by_method`: 搜索指定元素的方法，使用了 selenium 的 By 功能
	  - id: 以指定 id 搜尋
	  - css: 用 css 選擇器的方式搜尋
	  - xpath: 用 xpath 的語法搜尋
	  - link_text: 尋找文字連結為 `by_value` 的 `<a>` 元素
	  - partial_link_text: 尋找文字連結包含 `by_value` 的 `<a>` 元素
	  - name: 尋找 `name` 屬性的值為 `by_value` 的元素
	  - tag_name: 尋找 `<by_value>` 元素 
	  - class_name: 尋找 `class` 為 `by_value` 的元素
- `by_value`: 搭配 `by_method` 使用
- `result`: 會在每個 Test Case 的首行與帶有 `check_` 的 `action_type` 填入測試結果
	  - success: 成功
	  - failure: 失敗
	  - except failure: 通常發生在找不到指定元素的情況

### 驗證設定
![auth](https://raw.githubusercontent.com/Jackal-and-Platypus/SheetScraper/main/images/auth.png)

分頁名稱必須為 `auth`
- host url 的格子：plan 的頁面勾選 auth 後，會用該 Test Suite 的 host 搜尋 auth 的步驟
其他欄位與 Test Suite 分頁的步驟設定一致

### 執行程式
在 venv 或 conda 的環境中執行指令
```sh
python main.py
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## 版權聲明 License
使用 [MIT](https://github.com/Prysline/S2A1_restaurant/blob/main/LICENSE) License。

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## 致謝 Acknowledgments
* [town-intelligent/SheetScraper (github.com)](https://github.com/town-intelligent/SheetScraper) 提供初期代碼
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* [shields IO](https://shields.io/)

<p align="right">(<a href="#top">back to top</a>)</p>

