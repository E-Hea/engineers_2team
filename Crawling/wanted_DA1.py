from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime  # 크롤링 시간 추가를 위해 import
import pymysql

# 크롬드라이버 경로
chromedriver_path = 'C:\\choi\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'
service = Service(executable_path=chromedriver_path)
browser = webdriver.Chrome(service=service)

# 원티드 URL
browser.get("https://www.wanted.co.kr/wdlist?country=kr&job_sort=job.recommend_order&years=-1&locations=all")

job_name = "DA"
job_xpath1 = '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[29]'
job_xpath2 = '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[7]'

result = []

try:
    # 카테고리 열기 → 전체 → 직군 선택 → 필터 적용
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
        '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/button'))).click()
    time.sleep(1)

    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
        '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[1]/button[2]'))).click()
    time.sleep(1)

    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, job_xpath1))).click()
    time.sleep(1)

    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
        '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[3]/button[2]/span[2]'))).click()
    time.sleep(2)

    # 무한 스크롤
    while True:
        job_elements = browser.find_elements(By.XPATH, '//*[@id="__next"]/div[3]/div[2]/ul/li')
        total_jobs = len(job_elements)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_job_elements = browser.find_elements(By.XPATH, '//*[@id="__next"]/div[3]/div[2]/ul/li')
        new_total_jobs = len(new_job_elements)
        if new_total_jobs == total_jobs:
            break

    #개수설정
    max_jobs = 100
    for id in range(1, min(total_jobs, max_jobs) + 1):
        try:
            job_xpath_item = f'//*[@id="__next"]/div[3]/div[2]/ul/li[{id}]'
            element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, job_xpath_item)))
            element.click()

            def get_text_or_default(xpath):
                try:
                    return WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, xpath))).text.strip()
                except:
                    return "없음"

            # 기본 정보
            job_title = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/header/h1')
            company_name = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/header/div/div[1]/a')
            location = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/header/div/div[1]/span[2]')
            experience = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/header/div/div[1]/span[4]')

            # 상세보기 버튼 클릭
            try:
                view_more_button = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/button'))
                )
                view_more_button.click()
                time.sleep(1)
            except:
                print("상세보기 버튼 없음 또는 클릭 실패")

            # 상세 정보
            position_detail = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/span')
            main_tasks = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/div[1]/span')
            qualifications = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/div[2]/span')
            preferences = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/div[3]/span')
            benefits = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/div[4]/span')
            hiring_process = get_text_or_default('//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/div[5]/span')

            # 태그
            try:
                tags = browser.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/section/section/article[2]/ul').text.strip()
            except:
                tags = "없음"

            # 크롤링 일시
            crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            job_data = [
                id, job_title, job_name, company_name, location, experience,
                position_detail, main_tasks, qualifications, preferences,
                benefits, hiring_process, tags, crawl_time  # 여기서 시간 추가
            ]
            result.append(job_data)

            print(f"ID {id} in {job_name} - 크롤링 성공")

            browser.back()
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, job_xpath_item)))

        except Exception as e:
            print(f"Error on ID {id} in {job_name}: {str(e)}")
            continue

except Exception as e:
    print(f"Error processing {job_name}: {str(e)}")

# 결과 저장
save_path = f"C:\\Users\\thsk1\\Downloads\\{job_name}_jobs.csv"
df = pd.DataFrame(result, columns=[
    'ID', '제목','직무' , '회사', '위치', '경력',
    '포지션상세', '주요업무', '자격요건', '우대사항',
    '혜택 및 복지', '채용전형', '태그', '크롤링일시'  # 컬럼명에도 시간 추가
])
df.to_csv(save_path, index=False, encoding='utf-8-sig')
print(f"{job_name} 관련 CSV 파일이 {save_path}에 저장되었습니다.")

browser.close()

# 위 코드에서 job_name을 "데이터 엔지니어"로, job_xpath를
# '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[11]/p' 로 변경하면 됩니다.

# 위 코드에서 job_name을 "데이터 사이언티스트"로, job_xpath를
# '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[20]' 로 변경하면 됩니다.

# 위 코드에서 job_name을 "빅데이터 엔지니어"로, job_xpath를
# '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[22]' 로 변경하면 됩니다.

# 위 코드에서 job_name을 "DBA"로, job_xpath를
# '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[27]' 로 변경하면 됩니다.

# 위 코드에서 job_name을 "BI 엔지니어"로, job_xpath를
# '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[36]/p' 로 변경하면 됩니다.


# 위 코드에서 job_name을 "데이터 분석가"로, job_xpath를
# '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[2]/button[9]' 로 변경하고,
# 두 번째 버튼 클릭 부분을 아래처럼 변경하세요:
# WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH,
# '//*[@id="__next"]/div[3]/div[1]/section/div[1]/section/div/div/div[2]/div[2]/ul[1]/button[3]'))).

#=====================DB 저장=================
# DB 연결 설정
db_config = {
    'host': '127.0.0.1',
    'user': 'root',        # 본인 DB 사용자명
    'password': '',# 본인 비밀번호
    'database': 'engineers',# DB명 (ex: engineers)
    'charset': 'utf8mb4'
}

try:
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    insert_query = """
    INSERT IGNORE INTO wanted_jobs (
        job_id, job_title, job_name, company_name, location, experience,
        position_detail, main_tasks, qualifications, preferences,
        benefits, hiring_process, tags, crawl_time
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    cursor.executemany(insert_query, result)
    connection.commit()

    print(f"✅ 총 {cursor.rowcount} 건 새로 저장됨 (중복 항목은 무시됨)")

except Exception as e:
    print(f"❌ DB 저장 중 오류 발생: {e}")

finally:
    cursor.close()
    connection.close()
