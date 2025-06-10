import pymysql
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# DB 연결 정보
conn = pymysql.connect(
    host='',
    port=3306,
    user='root',
    password='',  # 비밀번호 입력
    db='engineers',
    charset='utf8mb4'
)

# 전처리 설정
phrases_to_remove = ['있는 분', '있으신 분', '수 있는', '고', '는', '를', '에', '대', '준하', '또', '이상', '바탕으로',
                     '을', '위', '이를', '해', '이에', '하는', '위해', '통해', '한', '이상', '혹은', '기반', '및', '용', '활',
                     '경험이', '수', '관련', '등', '에 대한', '가능한 분', '그에 준하는', '대한', '높은', '또는',
                     '가능하신 분', '보유하신 분', '분', '학', '야', '하', '졸', '하신', '사', '으로', '찾 있습니다', '의', '이', '이런', '가지신']

replacements = {
    '데이터': 'Data',
    '분석': 'Analysis',
    '빅데이터': 'BigData',
    '의사결정': 'communication',
    'DA': 'DataAnalysis',
    '커뮤니케이션': 'communication',
    '이커머스': 'ECommerce'
}

def remove_phrases(text):
    if pd.isna(text):
        return text
    for phrase in phrases_to_remove:
        text = text.replace(phrase, '')
    return text

def replace_then_truncate(text):
    if pd.isna(text):
        return text
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            return text.split(new)[0] + new
    return text

# 한글 폰트 경로 (Windows 기준, mac/Linux는 수정 필요)
font_path = "C:/Windows/Fonts/malgun.ttf"

# 직무코드별 워드클라우드 시각화 함수
def generate_wordcloud_for(code):
    query = f"""
    SELECT 우대사항
    FROM merged_jobs_preprocessing
    WHERE 직무코드 = '{code}'
    """
    df = pd.read_sql(query, conn)

    df['우대사항'] = df['우대사항'].apply(replace_then_truncate)
    df['우대사항'] = df['우대사항'].apply(remove_phrases)

    text = " ".join(df['우대사항'].dropna().astype(str))

    wordcloud = WordCloud(
        font_path=font_path,
        background_color='white',
        width=800,
        height=600
    ).generate(text)

    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'{code} 직무 - 우대사항 워드클라우드', fontsize=16)
    plt.show()

# --- 여기서 하나씩 실행해 주세요 ---
generate_wordcloud_for('DA')
generate_wordcloud_for('DS')
generate_wordcloud_for('ML')
generate_wordcloud_for('DE')

# 연결 종료
conn.close()
