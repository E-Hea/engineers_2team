from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime
import mysql.connector
import pymysql

# 드라이버 세팅
service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service)
wait = WebDriverWait(browser, 15)

# Jobplanet 메인 페이지 접속
browser.get("https://www.jobplanet.co.kr/job")
browser.implicitly_wait(10)

# 팝업 닫기 함수
"""
def close_popup():
    try:
        time.sleep(2)
        popup_close_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[class*="close"], button[class*="Close"]')))
        browser.execute_script("arguments[0].click();", popup_close_btn)
        print("팝업 닫기 완료")
    except Exception:
        try:
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
            browser.switch_to.frame(iframe)
            popup_close_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[class*="close"], button[class*="Close"]')))
            browser.execute_script("arguments[0].click();", popup_close_btn)
            browser.switch_to.default_content()
            print("팝업 닫기 완료 (iframe)")
        except Exception as e:
            print("팝업 없음 또는 닫기 실패:", e)

close_popup()"""

# '직종' 메뉴 클릭
job_category_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '직종')]")))
browser.execute_script("arguments[0].click();", job_category_btn)
time.sleep(1)

# 탭 클릭 함수 (데이터/개발 등)
def click_tab(tab_name):
    try:
        tab_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{tab_name}')]")))
        browser.execute_script("arguments[0].click();", tab_btn)
        time.sleep(0.5)
        print(f"'{tab_name}' 탭 클릭 완료")
    except Exception as e:
        print(f"'{tab_name}' 탭 클릭 실패: {e}")

# 직군 선택 함수
def select_job_roles(role_names):
    for role_name in role_names:
        try:
            label = wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//span[@class='jf_b1' and text()='{role_name}']")))
            input_box = label.find_element(By.XPATH, "./ancestor::label/input[@type='checkbox']")
            browser.execute_script("arguments[0].click();", input_box)
            print(f"[✓] '{role_name}' 선택 완료")
            time.sleep(0.5)
        except Exception as e:
            print(f"[X] '{role_name}' 선택 실패: {e}")

# 데이터 관련 직군 선택
click_tab("데이터")
data_roles = ["BI 엔지니어", "데이터 분석가", "데이터 사이언티스트", "데이터 엔지니어", "머신러닝 엔지니어", "빅데이터 엔지니어"]
select_job_roles(data_roles)

# 개발 탭에서 DBA 선택
click_tab("개발")
select_job_roles(["DBA(Database Admin.)"])

# 필터 적용
try:
    apply_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jf_h9")))
    apply_btn.click()
    print("필터 적용 버튼 클릭 완료")
    time.sleep(2)
except Exception as e:
    print(f"필터 적용 버튼 클릭 실패: {e}")


# 무한 스크롤 함수
def infinite_scroll():
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

infinite_scroll()

# 공고 링크 수집
job_elements = browser.find_elements(By.CSS_SELECTOR, "div.overflow-hidden.medium a")
job_links = [elem.get_attribute("href") for elem in job_elements]
print(f"총 {len(job_links)}개 공고 링크 수집 완료")

result = []

# 크롤링 함수 - 상세페이지에서 데이터 추출
def get_text_or_none(selector):
    try:
        return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector))).text.strip()
    except:
        return "없음"

for idx, link in enumerate(job_links, start=1): #여기 개수 수정하기
    try:
        browser.get(link)
        browser.implicitly_wait(10)

        url = browser.current_url
        company_name = get_text_or_none("span.company_name > a")
        position = get_text_or_none("div.apply_section > div.lft > h1.ttl")
        posit = get_text_or_none("div.recruitment-detail__box.recruitment-summary > dl > dd:nth-child(4)")
        work_exp = get_text_or_none("div.recruitment-detail__box.recruitment-summary > dl > dd:nth-child(6)")
        skills = get_text_or_none("div.recruitment-detail__box.recruitment-summary > dl > dd:nth-child(12)")
        task = get_text_or_none("div.block_job_posting > section > div:nth-child(3) > p")
        qualification = get_text_or_none("div.block_job_posting > section > div:nth-child(4) > p")
        preference = get_text_or_none("div.block_job_posting > section > div:nth-child(5) > p")
        process = get_text_or_none("div.block_job_posting > section > div:nth-child(6) > p")

        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data = [idx, url, company_name, position, posit, work_exp, skills, task, qualification, preference, process, crawl_time]
        result.append(data)
        print(f"[{idx}] 공고 크롤링 성공: {position} - {company_name}")

    except Exception as e:
        print(f"[{idx}] 공고 크롤링 실패: {e}\nURL: {link}")

# 데이터프레임 저장
columns = ['ID', 'URL', '회사명', '직업명', '직무', '경력', '스킬', '주요업무', '자격요건', '우대사항', '채용절차', '크롤링일시']
df = pd.DataFrame(result, columns=columns)

save_path = r"C:\Users\thsk1\Downloads\jobplanet.csv"
df.to_csv(save_path, index=False, encoding='utf-8-sig')
print(f"크롤링 데이터가 '{save_path}'에 저장되었습니다.")

browser.quit()

#=====================DB 저장=================
# MariaDB 연결
conn = pymysql.connect(
    host="127.0.0.1",  # 또는 다른 호스트
    user="root",
    password="",
    database="engineers",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # 크롤링한 URL 목록만 추출
        crawled_urls = [row[1] for row in result]  # row[1] = URL

        # DB에 이미 존재하는 URL 가져오기
        format_strings = ','.join(['%s'] * len(crawled_urls))
        cursor.execute(f"SELECT url FROM jobplanet WHERE url IN ({format_strings})", tuple(crawled_urls))
        existing_urls = set(row['url'] for row in cursor.fetchall())

        # 새로운 URL만 필터링
        new_data = [tuple(row[1:]) for row in result if row[1] not in existing_urls]


        if new_data:
            insert_sql = """
            INSERT INTO jobplanet (
                 url, company_name, position, posit, work_exp, skills, task, qualification, preference, process, crawl_time
            ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_sql, new_data)
            conn.commit()
            print(f"✅ DB에 {len(new_data)}개의 새 공고 저장 완료!")
        else:
            print("ℹ️ 이미 존재하는 공고만 있어서 DB에 저장할 항목이 없습니다.")

except Exception as e:
    print(f"❌ DB 저장 중 오류 발생: {e}")

finally:
    conn.close()
