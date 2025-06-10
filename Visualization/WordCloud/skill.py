import pymysql
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# MariaDB 연결
conn = pymysql.connect(
    host='',
    port=3306,
    user='root',
    password='',  # 비밀번호 입력
    db='engineers',
    charset='utf8mb4'
)

# 전처리용 치환 딕셔너리
replacements = {
    '파이썬': 'Python',
    'python': 'Python',
    '머신러닝': 'MachineLearning',
    'ml': 'MachineLearning',
    'ML': 'MachineLearning',
    'Machine Learning': 'MachineLearning',
    '딥러닝': 'DeepLearning',
    '딥 러닝': 'DeepLearning',
    'Deep Learning': 'DeepLearning',
    '아마존 웹 서비스': 'AWS',
    'C/c++': 'C, C++',
    'DataAnalysis': 'Data Analysis',
    '데이터': 'Data',
    '분석': 'Analysis',
    '인공지능': 'AI',
    '클라우드': 'Cloud'
}

# 전처리 함수
def preprocess_skills(text):
    if pd.isna(text):
        return ''
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# 워드클라우드 생성 함수
def generate_filtered_skill_wordcloud(code):
    query = f"""
        SELECT 스킬
        FROM merged_jobs_preprocessing
        WHERE 직무코드 = '{code}' AND 직무 NOT IN ('DA', 'DS', 'ML', 'DE')
    """
    df = pd.read_sql(query, conn)

    if df.empty:
        print(f"[{code}] 해당 조건을 만족하는 데이터가 없습니다.")
        return

    df['스킬'] = df['스킬'].apply(preprocess_skills)
    text = ' '.join(df['스킬'].dropna().astype(str))

    # 한글 폰트 경로 (Windows 기준)
    font_path = "C:/Windows/Fonts/malgun.ttf"

    wordcloud = WordCloud(
        font_path=font_path,
        width=800,
        height=800,
        background_color='white',
        max_words=100
    ).generate(text)

    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f"직무 != DA,DS,ML,DE AND 직무코드 = {code} - 스킬 워드클라우드", fontsize=14)
    plt.tight_layout()
    plt.show()

# 코드별 실행
for job_code in ['DA', 'DS', 'ML', 'DE']:
    generate_filtered_skill_wordcloud(job_code)

# 연결 종료
conn.close()
