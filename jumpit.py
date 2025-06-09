from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
from datetime import datetime
import mysql.connector
import pymysql


# 직무 리스트
job_titles = ["DBA", "빅데이터 엔지니어", "인공지능/머신러닝"]
total_data = []

# 반복: 직무별로 새 브라우저 창에서 크롤링
for job in job_titles:
    print(f"크롤링 시작: {job}")
    # 브라우저 새로 열기
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    browser.get('https://jumpit.saramin.co.kr/positions?sort=rsp_rate')
    time.sleep(1)

    # 필터 버튼 클릭
    buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.list_job_btn_wrap > button')))
    for btn in buttons:
        if btn.text.strip() == job:
            browser.execute_script("arguments[0].click();", btn)
            break
    time.sleep(2)

    # 스크롤 맨 아래까지
    def scroll_to_bottom():
        prev_height = browser.execute_script("return document.body.scrollHeight")
        while True:
            browser.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(1)
            curr_height = browser.execute_script("return document.body.scrollHeight")
            if curr_height == prev_height:
                break
            prev_height = curr_height

    scroll_to_bottom()

    # 공고 링크 수집
    job_links = []
    soup = BeautifulSoup(browser.page_source, "html.parser")
    job_elements = soup.find_all('div', class_='sc-d609d44f-0 grDLmW')

    for item in job_elements:
        a_tag = item.find('a')
        if a_tag and a_tag.has_attr('href'):
            job_link = a_tag['href']
            if job_link not in job_links:
                job_links.append(job_link)

    print(f"[{job}] 수집된 링크 수: {len(job_links)}")

    # 크롤링 개수 제한 (예: 3개만 크롤링) !!여기 수정하기!!
    #job_links = job_links[:5]

    # 상세 페이지 크롤링
    for link in job_links:
        browser.get(f'https://jumpit.saramin.co.kr{link}?sort=rate')
        time.sleep(2)

        for _ in range(5):
            ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.5)

        soup = BeautifulSoup(browser.page_source, "html.parser")

        # 제목 / 회사
        info_div = soup.find('div', class_='sc-923c3317-0 jIWuEG')
        title = info_div.find('h1').get_text(strip=True) if info_div and info_div.find('h1') else ''
        company = info_div.find('a', class_='name').find('span').get_text(strip=True) if info_div else ''

        # 경력 / 학력 / 위치
        info_dl = soup.find_all('dl', class_='sc-b12ae455-1 hvXrQd')
        experience = info_dl[0].find('dd').get_text(strip=True) if len(info_dl) > 0 else ''
        education = info_dl[1].find('dd').get_text(strip=True) if len(info_dl) > 1 else ''
        location = info_dl[-1].find('li').get_text(strip=True) if info_dl and info_dl[-1].find('li') else ''

        # 우대사항
        preferences_tag = soup.find('dt', string='우대사항')
        preferences = preferences_tag.find_next_sibling('dd').get_text(strip=True) if preferences_tag else ''

        # 주요업무
        tasks_tag = soup.find('dt', string='주요업무')
        tasks = tasks_tag.find_next_sibling('dd').get_text(strip=True) if tasks_tag else ''

        # 자격요건
        requirements_tag = soup.find('dt', string='자격요건')
        requirements = requirements_tag.find_next_sibling('dd').get_text(strip=True) if requirements_tag else ''

        # 기술스택
        tech_stack_divs = soup.select('dl:has(dt:-soup-contains("기술스택")) dd div.sc-d9de2de1-0')
        tech_stack = ', '.join(
            [div.find('img')['alt'] for div in tech_stack_divs if div.find('img')]) if tech_stack_divs else ''

        # 크롤링 일시
        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 추가됨

        # 데이터 저장
        total_data.append([job, title, company, location, experience, education,
                           tasks, requirements, preferences, tech_stack, crawl_time])

    # 브라우저 닫기
    browser.quit()
    print(f"크롤링 완료: {job}\n")

# CSV 저장
df = pd.DataFrame(total_data, columns=['직무', '제목', '회사 이름', '회사 위치', '경력', '학력',
                                       '주요업무', '자격요건', '우대사항', '기술스택','크롤링일시'])
save_path = r"C:\Users\thsk1\Downloads\점핏.csv"
df.to_csv(save_path, encoding='utf-8', index=False)

# 출력 옵션 및 샘플 출력
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
print(df.head())


#=====================================여기서 부터 DB
conn = pymysql.connect(
    host="127.0.0.1",        # 또는 다른 호스트
    user="root",
    password="",
    database="engineers",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        insert_query = """
        INSERT IGNORE INTO jumpit (
            job_title, post_title, company_name, location, experience, education,
            tasks, requirements, preferences, tech_stack, crawl_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        cursor.executemany(insert_query, total_data)
        conn.commit()

    print("DB에 데이터 저장 완료!")

except Exception as e:
    print(f"DB 저장 중 오류 발생: {e}")

finally:
    conn.close()

