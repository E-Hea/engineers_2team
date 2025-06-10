import pandas as pd
import pymysql
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# MariaDB 연결 정보 설정
host = ''  # 본인 환경에 맞게 수정
port = 3306
user = 'root'  # 본인 DB 계정
password = ''  # 본인 DB 비밀번호
database = 'engineers'

# DB 연결
conn = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database, charset='utf8mb4')

# 직무코드가 'ML'인 데이터만 쿼리로 가져오기 (자격요건 컬럼 포함)
query = "SELECT 자격요건 FROM merged_jobs_preprocessing WHERE 직무코드 = 'ML';"
df = pd.read_sql(query, conn)

conn.close()

# 전처리에 사용할 구문 및 대체 사전 정의
phrases_to_remove = ['있는 분', '있으신 분', '수 있는', '고', '는', '를', '에', '대', '준하','활', '또', '이상', '바탕으로',
                     'C C','가능', '포함', '용','C','과','을', '위', '이를', '해', '이에', '하는', '위해', '통해',
                     '한', '이상', '혹은', '기반', '및', '거나','런','가','업','자','무','력', '경험이', '수', '관련',
                     '등', '에 대한', '가능한 분', '그에 준하는', '대한', '높은', '또는', '준','능', '가능하신 분',
                     '보유하신 분','분','야','석','하','계신','졸','하신','가능자','사','으로', '찾 있습니다','의',
                     '이','이런','학','필','더욱','각','등','중','서','팀','도']

replacements = {
    '데이터': 'Data',
    '분석': 'Analysis',
    '빅데이터': 'BigData',
    '의사결정': 'communication',
    'DA': 'DataAnalysis',
    '커뮤니케이션':'communication',
    '딥러닝':'Deep Learning',
    '알고리즘':'algorithm',
    'ML' : '머신러닝',
    '컴퓨터 과학' :'Computer Science'
}

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

# 전처리 적용
df['자격요건'] = df['자격요건'].apply(replace_then_truncate)
df['자격요건'] = df['자격요건'].apply(remove_phrases)

# 텍스트 합치기 (워드클라우드용)
text = " ".join(df['자격요건'].dropna().astype(str))

# 워드클라우드 생성 및 시각화
font_path = 'C:/Windows/Fonts/malgun.ttf'  # 윈도우 한글폰트 경로 (필요시 변경)

wordcloud = WordCloud(font_path=font_path, background_color='white', width=800, height=600).generate(text)

plt.figure(figsize=(10,8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
