import openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# 매주 월요일마다 수정된 부분 있으면 그 부분 알려줘야됨
# 이전에 저장한 엑셀 파일을 열어서 이전 데이터 읽어
def previous_data(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    previous_data = []
    for row in ws.iter_rows(min_row=1, values_only=True):
        previous_data.append(row)
    return previous_data


# 업데이트된 데이터 실시간으로 크롤링해서 리스트에 넣어놓고
def recent_data():
    new_data = [] 
    url = 'https://www.exploit-db.com/'

    s = Service('/opt/homebrew/bin/chromedriver')
    driver = webdriver.Chrome(service=s)

    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(time_to_wait=5)

    while True:
        rows = driver.find_elements(By.XPATH, '/html/body/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/table/tbody/tr')

        for i in range(len(rows)):
            row = rows[i]
            columns = row.find_elements(By.TAG_NAME, 'td')
            date = columns[0].text
            title = columns[4].text
            platform = columns[6].text
            check = 'O' if platform == "Python" or platform == "payload" else ''

            link = columns[4].find_element(By.TAG_NAME, 'a')
            link.click()
            #eb_id, cve, code는 title 누르고 들어가서 내용 따로 크롤링해서 다시 뒤로가기해서 다음 내용 뽑게

            edb_id_element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div[1]/div[1]/div/div[1]/div/div/div/div[1]/h6')
            edb_id = edb_id_element.text
            cve_element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div[1]/div[1]/div/div[1]/div/div/div/div[2]/h6')
            cve = cve_element.text
            type_element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div/div/div/div[2]/h6/a')
            type = type_element.text
            code_element = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/div/div/div[2]/div[1]/div/pre/code')
            code = code_element.text
            
            try:
                new_data.append([date, title, edb_id, cve, type, code, platform, check])
                driver.back()

            except Exception as e:
                driver.back()

        next_button = driver.find_element(By.XPATH, '//*[@id="exploits-table_next"]/a')
        if 'disabled' in next_button.get_attribute('class'):
            break
        else:
            next_button.click()
            WebDriverWait(driver, 10).until(EC.staleness_of(rows[0]))

    driver.quit()
    return new_data


# 기존에 저장된 파일이랑 새로 크롤링한거 비교
def compare(previous_data, new_data):
    updated_data=[]
    for new_row in new_data:
        found = False
        for prev_row in previous_data:
            if new_row == prev_row:  # 코드 열 비교
                found = True
                break
        if not found:
            updated_data.append(new_row)
    return updated_data


#바뀐 데이터만 새로 엑셀파일에 저장
def save_updated_data(updated_data):
    if updated_data:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["DATE", "TITLE", "EDB-ID", "CVE", "TYPE", "CODE", "CATEGORY", "CHECK"])

        for row in updated_data:
            ws.append(row)
        wb.save("updated_data.xlsx")
        print("New updated data" )
    else:
        print("No updated data")
