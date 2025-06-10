import pandas as pd
import pymysql
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. MariaDB 연결 설정
conn = pymysql.connect(
    host='127.0.0.1',      # 또는 MariaDB 서버 주소
    port=3306,             # 기본 포트
    user='root',  # 사용자 계정
    password='2023111813',  # 비밀번호
    db='engineers',        # 데이터베이스명
    charset='utf8mb4'
)

# 2. DS 직무코드 필터링 후 '자격요건' 열 데이터 추출
query = "SELECT 자격요건 FROM merged_jobs_preprocessing WHERE 직무코드 = 'DS';"
df = pd.read_sql(query, conn)
conn.close()

# 3. 전처리 대상 문구 및 교체 사전
phrases_to_remove = ['있는 분', '있으신 분', '수 있는', '고', '는', '를', '에', '대', '준하', '또', '이상', '바탕으로',
                     '을', '위', '이를', '해', '이에', '하는', '위해', '통해', '한', '이상', '혹은', '기반', '및',
                     '경험이', '수', '관련', '등', '에 대한', '가능한 분', '그에 준하는', '대한', '높은', '또는', '싶어요', '함께'
                     '가능하신 분', '보유하신 분','분','야','석','하','계신','졸','하신','가능자','사','으로', '찾 있습니다','의','이','이런','학','필','더욱','각','등','중','서','팀','도']

replacements = {
    '데이터': 'Data',
    '분석': 'Analysis',
    '빅데이터': 'BigData',
    '의사결정': 'communication',
    'DA': 'DataAnalysis',
    '커뮤니케이션':'communication',
    '딥러닝':'Deep Learning',
    '알고리즘':'algorithm',
    'ML' : '머신러닝'
}

# 4. 전처리 함수 정의
def replace_then_truncate(text):
    if pd.isna(text):
        return text
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            return text.split(new)[0] + new
    return text

def remove_phrases(text):
    if pd.isna(text):
        return text
    for phrase in phrases_to_remove:
        text = text.replace(phrase, '')
    return text

# 5. 전처리 적용
df['자격요건'] = df['자격요건'].apply(replace_then_truncate)
df['자격요건'] = df['자격요건'].apply(remove_phrases)

# 6. 워드클라우드 생성용 텍스트 추출
text = " ".join(df['자격요건'].dropna().astype(str))

# 7. 한글 폰트 경로 설정 (윈도우 예시)
font_path = "C:/Windows/Fonts/malgun.ttf"

# 8. 워드클라우드 생성 및 시각화
wordcloud = WordCloud(font_path=font_path, background_color='white', width=800, height=600).generate(text)

plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('자격요건 워드클라우드 - DS 직무')
plt.show()
