# image_downloader.py
import os
import sys
import time
import requests
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Headless 모드 사용을 위한 옵션 추가
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # 새로운 방식으로 요소를 찾기 위해 필요
from bs4 import BeautifulSoup

# 폴더 생성 함수
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# 이미지 다운로드 함수
def download_image(image_url, folder_name, image_number):
    try:
        # Base64 데이터 URI를 처리하는 부분
        if image_url.startswith("data:image"):
            header, encoded = image_url.split(",", 1)
            img_data = base64.b64decode(encoded)
            with open(f"{folder_name}/image_{image_number}.jpg", 'wb') as img_file:
                img_file.write(img_data)
        else:
            # 일반적인 URL에서 이미지 다운로드
            img_data = requests.get(image_url).content
            with open(f"{folder_name}/image_{image_number}.jpg", 'wb') as img_file:
                img_file.write(img_data)
    except Exception as e:
        print(f"이미지 다운로드 실패: {e}")

# 메인 크롤링 함수
def image_crawler(search_term, num_images):
    folder_name = f"{search_term}_images"
    create_folder(folder_name)

    # Selenium을 이용하여 Google 이미지 검색

    service = Service(executable_path="/usr/bin/chromedriver")
    options = webdriver.ChromeOptions()

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 새로운 헤드리스 모드
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # 사용자 에이전트 설정
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    )

    # Chrome WebDriver 설정
    driver = webdriver.Chrome(service=service,options=chrome_options)  # ChromeDriver 경로를 지정해 주세요.
    
    # driver = webdriver.Chrome()  # ChromeDriver 경로를 지정해 주세요.
    
    search_url = f"https://www.google.com/search?q={search_term}&source=lnms&tbm=isch"
    driver.get(search_url)

    # 스크롤하여 이미지 로드
    last_height = driver.execute_script("return document.body.scrollHeight")
    while len(driver.find_elements(By.CSS_SELECTOR, "img")) < num_images:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # BeautifulSoup을 이용해 이미지 태그 수집
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    images = soup.find_all("img", limit=num_images)

    image_number = 1
    for img in images:
        image_url = img.get("src")
        if image_url:
            download_image(image_url, folder_name, image_number)
            image_number += 1

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python image_downloader.py [검색어] [이미지 수]")
        sys.exit(1)

    search_term = sys.argv[1]
    num_images = int(sys.argv[2])

    image_crawler(search_term, num_images)
