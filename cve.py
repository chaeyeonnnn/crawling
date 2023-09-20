'''
  # 페이지가 로드될 때까지 대기 (필요에 따라 조절)


            if response.status_code == 200:
                # 파일 저장
                with open(os.path.join('CVE_files', file_name), 'wb') as file:
                    file.write(response.content)
                print(f'Downloaded: {file_name}')

                time.sleep(10)

                with open(os.path.join('CVE_files', file_name), 'r', encoding='utf-8') as file:
                    file_content = file.read()
            
                # 데이터 프레임에 추가
                result_df = result_df.append({'File Name': file_name, 'Content': file_content}, ignore_index=True)

                #파일로 저장
                result_df.to_excel('CVE_data_2023.xlsx', index=False)



from inspect import getfile
import os
import re
from urllib import request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import requests

# step 1
#https://github.com/CVEProject/cvelistV5/tree/main/cves/2023
#https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx
#https://github.com/CVEProject/cvelistV5/blob/main/cves/2023/0xxx/CVE-2023-0001.json
# 이 라인대로 타고 타고 들어가서 크롤링을 해야함

# step 2
#//*[@id="folder-row-1"]/td[2]/div/div/h3/div
#//*[@id="folder-row-5"]/td[2]/div/div/h3/div
# 이 라인대로 0xxx 1xxx 20xxx ... 이렇게 눌러서 크롤링을 해야됨 

#이게 차례대로 0001, 0002, 0003.json 파일의 xpath
#//*[@id=":r2k:"]/span/span
#//*[@id=":r2n:"]/span/span
#//*[@id=":r2q:"]/span/span


# step 3
#//*[@id="repos-sticky-header"]/div[1]/div[2]/div[2]/div[1]/div[1]/span/button/svg
# 이게 파일 다운로드 버튼 XPATH 
# //*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/main/div[2]/div/div[1]/div/div[1]/div/div[1]/h2/button[1]/span
# 이게 뒤로가기 버튼


import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup

# Chrome 웹 드라이버를 실행
s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.maximize_window()

# GitHub 사이트로 이동
github_url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves/2023'
driver.get(github_url)

# 결과를 저장할 디렉토리 생성
output_directory = 'CVE_files_2023'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

crawled_data = []

# GitHub 사이트를 탐색하면서 파일 다운로드
while True:
    try:
        # 현재 페이지의 HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        file_elements = soup.find_all('a', class_='js-navigation-open link-gray-dark')
        for file_element in file_elements:
            file_name = file_element.get_text()
            file_url = file_element['href']
            
            # 파일의 확장자가 .json인 경우에만 다운로드 수행
            if file_name.endswith('.json'):
                # 파일 다운로드를 위해 해당 파일 페이지로 이동
                driver.get('https://github.com' + file_url)
                time.sleep(2)  # 페이지 로딩을 기다림
                
                # 파일 다운로드 버튼을 찾아 클릭
                try:
                    download_button = driver.find_element(By.XPATH, '//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/main/div[2]/div/div[1]/div/div[1]/div/div[1]/h2/button[1]/span')
                    download_button.click()
                except NoSuchElementException:
                    print(f"파일 다운로드 버튼을 찾을 수 없습니다: {file_name}")
                
                # 다운로드한 파일을 디렉토리에 이동 및 이름 변경
                time.sleep(5)  # 다운로드가 완료될 때까지 대기
                downloaded_file_name = max([os.path.join(output_directory, f) for f in os.listdir(output_directory)], key=os.path.getctime)
                new_file_name = os.path.join(output_directory, file_name)
                os.rename(downloaded_file_name, new_file_name)
                
                print(f"다운로드 및 저장 완료: {new_file_name}")
                
                # 결과 DataFrame에 추가
                crawled_data.append({'File Name': file_name, 'Content': new_file_name})
        
        # "Load more" 버튼이 있는지 확인하여 클릭
        load_more_button = driver.find_element(By.PARTIAL_LINK_TEXT, 'Load more')
        load_more_button.click()
        time.sleep(2)  # 페이지 로딩을 기다림
        
    except NoSuchElementException:
        print("더 이상 파일이 없거나 페이지 로딩이 완료되었습니다.")
        break
    except TimeoutException:
        print("페이지 로딩이 타임아웃 되었습니다.")

result_df = pd.DataFrame(crawled_data)


# 결과를 엑셀 파일로 저장
result_excel_file = os.path.join(output_directory, 'CVE_files_2023.xlsx')
result_df.to_excel(result_excel_file, index=False)
print(f"저장 완료{result_excel_file}")

# 크롬 드라이버 종료
driver.quit()

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import openpyxl

s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.maximize_window()

github_url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves/2023'
driver.get(github_url)

# 결과 저장할 디렉토리 생성
output_directory = 'CVE_files_2023'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

crawled_data = []  

# GitHub 사이트를 탐색하면서 파일 다운로드
while True:
    try:
        # 현재 페이지의 HTML 파싱
        page_source = "https://github.com/CVEProject/cvelistV5/tree/main/cves"
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        file_elements = soup.find_all('a', class_='js-navigation-open link-gray-dark')
        for file_element in file_elements:
            file_name = file_element.get_text()
            file_url = file_element['href']
            
            # 파일의 확장자가 .json인 경우에만 다운로드 수행
            if file_name.endswith('.json'):
                # 파일 다운로드를 위해 해당 파일 페이지로 이동
                driver.get('https://github.com' + file_url)
                time.sleep(2)  # 페이지 로딩을 기다림
                
                # 파일 다운로드 버튼을 찾아 클릭
                try:
                    download_button = driver.find_element(By.XPATH, '//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/main/div/section[2]/div/div[1]/div[1]/div[2]/div/div/div[3]/div[2]/div[1]/span/a')
                    download_button.click()
                except NoSuchElementException:
                    print(f"다운로드 버튼 없음: {file_name}")
                
                # 다운로드한 파일을 디렉토리에 이동 및 이름 변경
                time.sleep(5)  # 다운로드가 완료될 때까지 대기
                downloaded_file_name = max([os.path.join(output_directory, f) for f in os.listdir(output_directory)], key=os.path.getctime)
                new_file_name = os.path.join(output_directory, file_name)
                os.rename(downloaded_file_name, new_file_name)
                
                print(f"다운로드 및 저장 완료: {new_file_name}")
                
                # 결과 리스트에 추가
                crawled_data.append({'File Name': file_name, 'Content': new_file_name})
        
        # "Load more" 버튼이 있는지 확인하여 클릭
        load_more_button = driver.find_element(By.PARTIAL_LINK_TEXT, 'Load more')
        load_more_button.click()
        time.sleep(2)  # 페이지 로딩을 기다림
        
    except NoSuchElementException:
        print("파일없다")
        break
    except TimeoutException:
        print("타임아웃")

result_df = pd.DataFrame(crawled_data)

# 결과를 엑셀 파일로 저장
result_excel_file = os.path.join(output_directory, 'CVE_files_2023.xlsx')
result_df.to_excel(result_excel_file, index=False)
print(f"{result_excel_file}에 저장 완료")


# 크롬 드라이버 종료
driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import StaleElementReferenceException

from selenium.common.exceptions import NoSuchElementException, TimeoutException

import openpyxl

wb = openpyxl.Workbook()
ws = wb.active

s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)


url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves'

driver.get(url)
driver.maximize_window()
driver.implicitly_wait(time_to_wait=5)

year_element = driver.find_element(By.XPATH, '//*[@id="folder-row-25"]/td[2]/div/div/h3/div/a')
year_element.click()
try:
    add_element = driver.find_element(By.XPATH, '//*[@id="folder-row-1"]/td[2]/div/div/h3/div/a')
    add_element.click()
except StaleElementReferenceException:
    # 예외 처리: 요소가 더 이상 사용 가능하지 않을 때 다시 찾기
    add_element = driver.find_element(By.XPATH, '//*[@id="folder-row-1"]/td[2]/div/div/h3/div/a')  # 다시 찾기
    add_element.click()

i = 1
while True:
    try:
        path = """//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/main/div[2]/div/div[3]"""
        rows = driver.find_elements(By.XPATH,path)
        for i in range(len(rows)):
            row = rows[i]
            # 페이지 소스 가져오기
            page_source = driver.page_source

            # 파일 이름과 내용 엑셀에 추가
            ws.append([f'CVE_data_{i}', page_source])
            print(f"Data saved for CVE_data_{i}")
            
            back_element_xpath = '//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/main/div[2]/div/div[1]/div/div[1]/div/div[1]/h2/button[1]/span'
            try:
                next_element = driver.find_element(By.XPATH, back_element_xpath)
                next_element.click()
                time.sleep(2)
                i += 1
            except NoSuchElementException:
                pass

    except StaleElementReferenceException:
        break


wb.save("cve_data.xlsx")
driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import openpyxl


wb = openpyxl.Workbook()
ws = wb.active


s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)

url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves'

driver.get(url)
driver.maximize_window()
driver.implicitly_wait(time_to_wait=5)

year_element = driver.find_element(By.XPATH, '//*[@id="folder-row-25"]/td[2]/div/div/h3/div/a')
year_element.click()
try:
    add_element = driver.find_element(By.XPATH, '//*[@id="folder-row-1"]/td[2]/div/div/h3/div/a')
    add_element.click()
except StaleElementReferenceException:
    # 예외 처리: 요소가 더 이상 사용 가능하지 않을 때 다시 찾기
    add_element = driver.find_element(By.XPATH, '//*[@id="folder-row-1"]/td[2]/div/div/h3/div/a')  # 다시 찾기
    add_element.click()

i = 1
while True:
    try:
        # 페이지 소스 가져오기
        page_source = driver.page_source

        # 파일 이름과 내용 엑셀에 추가
        ws.append([f'CVE_data_{i}', page_source])
        print(f"Data saved for CVE_data_{i}")
        
        back_element_xpath = '//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/main/div[2]/div/div[1]/div/div[1]/div/div[1]/h2/button[1]/span'
        try:
            next_element = driver.find_element(By.XPATH, back_element_xpath)
            next_element.click()
            time.sleep(2)
            i += 1
        except NoSuchElementException:
            break  # 더 이상 다음 페이지가 없을 때 반복문 종료

    except StaleElementReferenceException:
        break

wb.save("cve_data.xlsx")
driver.quit()


import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import openpyxl

s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.maximize_window()

github_url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves/2023'
driver.get(github_url)

# 결과 저장할 디렉토리 생성
output_directory = 'CVE_files_2023'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

crawled_data = []  

# GitHub 사이트를 탐색하면서 파일 다운로드
while True:
    try:
        # 현재 페이지의 HTML 파싱
        page_source = "https://github.com/CVEProject/cvelistV5/tree/main/cves"
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        file_elements = soup.find_all('a', class_='js-navigation-open link-gray-dark')
        for file_element in file_elements:
            file_name = file_element.get_text()
            file_url = file_element['href']
            
            # 파일의 확장자가 .json인 경우에만 다운로드 수행
            if file_name.endswith('.json'):
                # 파일 다운로드를 위해 해당 파일 페이지로 이동
                driver.get('https://github.com' + file_url)
                time.sleep(2)  # 페이지 로딩을 기다림
                
                # 파일 다운로드 버튼을 찾아 클릭
                try:
                    download_button = driver.find_element(By.XPATH, '//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/main/div/section[2]/div/div[1]/div[1]/div[2]/div/div/div[3]/div[2]/div[1]/span/a')
                    download_button.click()
                except NoSuchElementException:
                    print(f"다운로드 버튼 없음: {file_name}")
                
                # 다운로드한 파일을 디렉토리에 이동 및 이름 변경
                time.sleep(5)  # 다운로드가 완료될 때까지 대기
                downloaded_file_name = max([os.path.join(output_directory, f) for f in os.listdir(output_directory)], key=os.path.getctime)
                new_file_name = os.path.join(output_directory, file_name)
                os.rename(downloaded_file_name, new_file_name)
                
                print(f"다운로드 및 저장 완료: {new_file_name}")
                
                # 결과 리스트에 추가
                crawled_data.append({'File Name': file_name, 'Content': new_file_name})
        
        # "Load more" 버튼이 있는지 확인하여 클릭
        load_more_button = driver.find_element(By.PARTIAL_LINK_TEXT, 'Load more')
        load_more_button.click()
        time.sleep(2)  # 페이지 로딩을 기다림
        
    except NoSuchElementException:
        print("파일없다")
        break
    except TimeoutException:
        print("타임아웃")

result_df = pd.DataFrame(crawled_data)

# 결과를 엑셀 파일로 저장
result_excel_file = os.path.join(output_directory, 'CVE_files_2023.xlsx')
result_df.to_excel(result_excel_file, index=False)
print(f"{result_excel_file}에 저장 완료")


# 크롬 드라이버 종료
driver.quit()


import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import json

# Chrome 웹 드라이버를 실행
s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.maximize_window()
time.sleep(10)

# GitHub API 엔드포인트 및 토큰 설정
base_url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves'
token = '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'

# 다운로드할 연도 설정
year = 2023

# 결과를 저장할 디렉토리 생성
if not os.path.exists('CVE_files'):
    os.makedirs('CVE_files')

year_url = f'{base_url}{year:04d}'
headers = {'Authorization': f'token {token}'}
    
# 해당 연도의 폴더 내 파일 목록 가져오기
response = requests.get(year_url, headers=headers)


try:
    data = response.json()
    result_df = pd.DataFrame(columns=['File Name', 'Content'])

    for item in data:
        if item['type'] == 'file':
            # 파일 URL 생성
            file_url = item['download_url']
            file_name = item['name']
            
            # 파일 다운로드
            response = requests.get(file_url, headers=headers)
            
            try:
                json_data = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"JSON 디코딩 오류: {str(e)}")
                continue
            
            cve_number = json_data["CVE_data_meta"]["ID"]
            excel_file_name = os.path.join("CVE_files", f"CVE-{year}-{cve_number}.xlsx")
            df = pd.json_normalize(json_data)
            df.to_excel(excel_file_name, index=False)

except json.decoder.JSONDecodeError:
    # JSON 디코딩 오류 처리
    print("JSON decoding error. Response content:")
    print(response.text)


# 크롬 드라이버 종료
driver.quit()

import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import json

# Chrome 웹 드라이버를 실행
s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.maximize_window()
time.sleep(10)

# GitHub API 엔드포인트 및 토큰 설정
base_url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves'
token = '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'

# 다운로드할 연도 설정
year = 2023

# 결과를 저장할 디렉토리 생성
if not os.path.exists('CVE_files'):
    os.makedirs('CVE_files')

year_url = f'{base_url}{year:04d}'
headers = {'Authorization': f'token {token}'}

# 해당 연도의 폴더 내 파일 목록 가져오기
response = requests.get(year_url, headers=headers)

try:
    data = response.json()
    result_df = pd.DataFrame(columns=['File Name', 'Content'])

    for item in data:
        if item['type'] == 'file':
            # 파일 URL 생성
            file_url = item['download_url']
            file_name = item['name']

            # 파일 다운로드
            response = requests.get(file_url, headers=headers)

            try:
                json_data = json.loads(response.text)  # 수정: response를 text로 변환
            except json.JSONDecodeError as e:
                print(f"JSON 디코딩 오류: {str(e)}")
                continue

            cve_number = json_data["CVE_data_meta"]["ID"]
            csv_file_name = os.path.join("CVE_files", f"CVE-{year}-{cve_number}.csv")  # 수정: 확장자 변경
            df = pd.json_normalize(json_data)

            # CSV 파일로 저장
            df.to_csv("cve.csv", encoding='utf-8-sig') 

except json.decoder.JSONDecodeError:
    # JSON 디코딩 오류 처리
    print("JSON decoding error. Response content:")
    print(response.text)

# 크롬 드라이버 종료
driver.quit()


import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import json

# Chrome 웹 드라이버를 실행
s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.maximize_window()
time.sleep(10)

# GitHub API 엔드포인트 및 토큰 설정
base_url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves'
token = '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'

# 다운로드할 연도 설정
year = 2023

# 결과를 저장할 디렉토리 생성
if not os.path.exists('CVE'):
    os.makedirs('CVE')

year = f'{base_url}/{year:04d}'
headers = {'Authorization': f'token {token}'}

# 해당 연도의 폴더 내 파일 목록 가져오기
response = requests.get(year, headers=headers)

# 파일 정보를 저장할 리스트 생성
file_data_list = []

try:
    data = response.json()

    for item in data:
        if item['type'] == 'file':
            # 파일 URL 생성
            file_url = item['download_url']
            file_name = item['name']

            # 파일 다운로드
            response = requests.get(file_url, headers=headers)

            try:
                json_data = json.loads(response.text) 
                print("성공적으로 디코딩")
                cve_number = json_data["CVE_data_meta"]["ID"]
                file_data_list.append({'File Name': file_name, 'Content': json_data})

            except json.JSONDecodeError as e:
                print(f"JSON 디코딩 오류: {str(e)}")
                continue
            
except json.decoder.JSONDecodeError:
    # JSON 디코딩 오류 처리
    print("JSON decoding error. Response content:")
    print(response.text)

# 크롬 드라이버 종료
driver.quit()

# 리스트 --> 데이터프레임
result_df = pd.DataFrame(file_data_list)

# CSV 파일로 저장
result_df.to_csv("cve_data.csv", index=False, encoding='utf-8-sig')
'''


import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import json

# Chrome 웹 드라이버를 실행
s = Service('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.maximize_window()
time.sleep(10)

# GitHub API 엔드포인트 및 토큰 설정
base_url = 'https://github.com/CVEProject/cvelistV5/tree/main/cves'
token = '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'

# 다운로드할 연도 설정
year = 2023

# 결과를 저장할 디렉토리 생성
if not os.path.exists('CVE_files'):
    os.makedirs('CVE_files')

year_url = f'{base_url}{year:04d}'
headers = {'Authorization': f'token {token}'}

# 해당 연도의 폴더 내 파일 목록 가져오기
response = requests.get(year_url, headers=headers)

try:
    data = response.json()
    result_df = pd.DataFrame(columns=['File Name', 'Content'])

    for item in data:
        if item['type'] == 'file':
            # 파일 URL 생성
            file_url = item['download_url']
            file_name = item['name']

            # 파일 다운로드
            response = requests.get(file_url, headers=headers)

            try:
                json_data = json.loads(response.text)  # 수정: response를 text로 변환
            except json.JSONDecodeError as e:
                print(f"JSON 디코딩 오류: {str(e)}")
                continue

            cve_number = json_data["CVE_data_meta"]["ID"]
            csv_file_name = os.path.join("CVE_files", f"CVE-{year}-{cve_number}.csv")  # 수정: 확장자 변경
            df = pd.json_normalize(json_data)

            # CSV 파일로 저장
            df.to_csv("cve.csv", encoding='utf-8-sig') 

except json.decoder.JSONDecodeError:
    # JSON 디코딩 오류 처리
    print("JSON decoding error. Response content:")
    print(response.text)

# 크롬 드라이버 종료
driver.quit()
