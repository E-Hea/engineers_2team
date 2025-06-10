import pymysql
import pandas as pd
import re
from konlpy.tag import Okt
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from tqdm import tqdm
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis

# 1️⃣ MariaDB에서 데이터 불러오기
connection = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='2023111813',
    database='engineers',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        sql = "SELECT 직무코드, 자격요건, 우대사항 FROM merged_jobs_preprocessing"
        cursor.execute(sql)
        results = cursor.fetchall()
        df = pd.DataFrame(results)

finally:
    connection.close()

print(f"불러온 데이터 건수: {len(df)}개")

# 2️⃣ 텍스트 전처리 함수
okt = Okt()

stop_words = set([
    '및', '등', '관련', '위해', '대한', '보유', '가능', '업무', '이상', '수', '분야',
    '경험', '우대', '필수', '자격', '능력', '개발', '사용', '이해', '활용'
])

def preprocess(text):
    if text is None:
        text = ""
    text = re.sub(r'[^가-힣a-zA-Z\s]', ' ', text)
    tokens = okt.nouns(text)
    tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
    return tokens

# 3️⃣ 직무별로 자격요건/우대사항 따로 처리
job_types = ['DS', 'DE', 'ML', 'DA']
sections = {'자격요건': 'requirement', '우대사항': 'preference'}

for job in job_types:
    print(f"\n\n=== [{job}] 직무 LDA 시작 ===\n")
    job_df = df[df['직무코드'] == job].copy()

    for column, tag in sections.items():
        print(f"\n--- [{job}] {column} 분석 중 ---")

        texts = []
        for doc in tqdm(job_df[column].fillna(''), desc=f"{job} - {column} 전처리"):
            tokens = preprocess(doc)
            texts.append(tokens)

        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]

        if len(dictionary.token2id) == 0:
            print(f"[{job} - {column}] 유효한 토큰이 부족하여 건너뜀")
            continue

        lda_model = LdaModel(corpus=corpus, num_topics=5, id2word=dictionary, passes=10, random_state=42)

        print(f"\n[{job} - {column}] LDA 결과:")
        for idx, topic in lda_model.print_topics(-1):
            print(f"Topic {idx}: {topic}")

        vis_data = gensimvis.prepare(lda_model, corpus, dictionary)
        filename = f'{job}_{tag}_lda_visualization.html'
        pyLDAvis.save_html(vis_data, filename)
        print(f"[{job} - {column}] 시각화 저장 완료 → {filename}")

    print("\n\n========================\n")