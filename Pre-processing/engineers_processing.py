import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine

# DB 연결 정보 설정
engine = create_engine("mysql+pymysql://root:@127.0.0.1/engineers")

# 데이터 로딩
df = pd.read_sql("SELECT * FROM merged_jobs", con=engine)


# -----------------------------
# 1. 직무 분류 전처리
# -----------------------------

# 직무 키워드 기반 분류 함수 정의
def classify_job(text):
    if pd.isna(text):
        return np.nan
    text = text.lower()
    if any(keyword in text for keyword in ['머신러닝', 'ml', 'modeling']):
        return 'ML'
    elif any(keyword in text for keyword in ['데이터 사이언티스트', 'ds', '통계', '분석모델']):
        return 'DS'
    elif any(keyword in text for keyword in ['데이터 분석', 'data analyst', '분석', '리포트', 'dba', 'da']):
        return 'DA'
    elif any(keyword in text for keyword in ['데이터 엔지니어', 'pipeline', 'etl', 'de']):
        return 'DE'
    else:
        return '기타'


# '직무' 또는 '직업명' 열에서 분류
df['직무코드'] = df['직무'].combine_first(df['직업명']).apply(classify_job)


# -----------------------------
# 2. 경력 범위 → 중앙값으로 변환
# -----------------------------

def parse_experience(x):
    if pd.isna(x):
        return np.nan

    x = x.strip().lower().replace(" ", "")

    # 무관, 경력무관, 신입~ 경력10년 같은 표현 → 0
    if '무관' in x or '경력무관' in x or '신입~' in x:
        return 0.0

    # 신입 단독 → 0
    if x == '신입':
        return 0.0

    # 신입 이상 → 1
    if '신입이상' in x:
        return 1.0

    # 신입-경력n년 → n/2 (예: 신입-경력4년)
    match = re.search(r'신입.*경력(\d+)', x)
    if match:
        n = int(match.group(1))
        return round(n / 2, 1)

    # 범위 (예: 1~3, 2-5) → 중앙값
    match = re.search(r'(\d+)[~\-](\d+)', x)
    if match:
        n1, n2 = map(int, match.groups())
        return round((n1 + n2) / 2, 1)

    # 숫자만 있는 경우 (예: 5, 10) → 숫자 추출
    match = re.search(r'(\d+)', x)
    if match:
        return float(match.group(1))

    return np.nan

df['경력연차'] = df['경력'].apply(parse_experience)

# -----------------------------
# 3. 전처리 결과 저장
# -----------------------------

# 필요한 컬럼만 선택해 저장
save_cols = ['회사명', '직업명', '직무', '직무코드', '경력', '경력연차', '학력', '스킬', '주요업무', '자격요건', '우대사항', '크롤링일시']
df_preprocessed = df[save_cols]

# MySQL에 저장
df_preprocessed.to_sql("merged_jobs_preprocessing", con=engine, if_exists='replace', index=False)

# CSV 저장 경로 설정
save_path = "C:\\Users\\thsk1\\Downloads\\merged_jobs_preprocessing.csv"
df_preprocessed.to_csv(save_path, index=False, encoding='utf-8-sig')

print("✅ 전처리 완료: MySQL + CSV 파일 저장 성공!")
