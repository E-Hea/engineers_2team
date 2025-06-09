import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text

# DB 연결 설정
user = 'root'
password = ''
host = '127.0.0.1'
port = 3306
database = 'engineers'
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

def load_and_map(table_name):
    df = pd.read_sql_table(table_name, con=engine)

    if table_name == 'jumpit':
        df.rename(columns={
            'company_name': '회사명',
            'post_title': '직업명',
            'job_title': '직무',
            'experience': '경력',
            'education': '학력',
            'tech_stack': '스킬',
            'tasks': '주요업무',
            'requirements': '자격요건',
            'preferences': '우대사항',
            'crawl_time': '크롤링일시',
        }, inplace=True)

    elif table_name == 'jobplanet':
        df.rename(columns={
            'company_name': '회사명',
            'position': '직업명',
            'posit': '직무',
            'work_exp': '경력',
            'skills': '스킬',
            'task': '주요업무',
            'qualification': '자격요건',
            'preference': '우대사항',
            'crawl_time': '크롤링일시',
        }, inplace=True)
        df['학력'] = '학력무관'  # jobplanet에는 학력 없음

    elif table_name == 'wanted_jobs':
        df.rename(columns={
            'company_name': '회사명',
            'job_title': '직업명',
            'job_name': '직무',
            'experience': '경력',
            'main_tasks': '주요업무',
            'qualifications': '자격요건',
            'preferences': '우대사항',
            'tags': '스킬',
            'crawl_time': '크롤링일시',
        }, inplace=True)
        df['학력'] = '학력무관'

    else:
        raise ValueError('Unknown table name')

    # 공통 컬럼만 추출
    common_columns = ['회사명', '직업명', '직무', '경력', '학력', '스킬', '주요업무', '자격요건', '우대사항', '크롤링일시']
    return df[common_columns]


# 1) merged_jobs에서 가장 최근 크롤링일시 조회
with engine.connect() as conn:
    query = text("SELECT MAX(크롤링일시) FROM merged_jobs")
    last_crawl_time = conn.execute(query).scalar()

if last_crawl_time is None:
    # merged_jobs가 비어있으면 아주 오래된 날짜로 설정
    last_crawl_time = '1900-01-01 00:00:00'

# 2) 원본 테이블에서 last_crawl_time 이후 데이터만 불러와 병합
dfs = []
for table in ['jumpit', 'jobplanet', 'wanted_jobs']:
    df = load_and_map(table)
    df_new = df[df['크롤링일시'] > last_crawl_time]
    dfs.append(df_new)

new_data = pd.concat(dfs, ignore_index=True)

if new_data.empty:
    print("새로운 데이터가 없습니다.")
else:
    # 3) 중복 제거 (회사명, 직업명, 직무 기준), 최근 데이터 유지
    new_data.drop_duplicates(subset=['회사명', '직업명', '직무'], keep='last', inplace=True)

    # 4) merged_jobs에 신규 데이터 삽입
    new_data.to_sql('merged_jobs', con=engine, if_exists='append', index=False)
    print(f"새로운 데이터 {len(new_data)}건이 merged_jobs에 추가되었습니다.")
