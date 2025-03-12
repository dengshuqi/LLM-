import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import os

# 文件夹路径
csv_folder = './数据表/sample_entityTable_array/'
document_path = './博客案例集/'  # 这里替换为实际的文档数据存储路径

# 停用词列表（可以根据实际情况扩展）
stop_words = set([
    '的', '是', '在', '和', '了', '我', '有', '就', '不', '人', '都', '说'
])

# 读取文档内容并统一小写
document_contents = {}
for filename in os.listdir(document_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(document_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().lower()  # 转换为小写
            document_title = filename
            document_contents[document_title] = content

# 遍历文件夹中的所有CSV文件，收集所有实体词汇并添加到jieba词典中
all_entities = set()
for filename in os.listdir(csv_folder):
    if filename.startswith('sample_entityTable_') and filename.endswith('.csv'):
        csv_file = os.path.join(csv_folder, filename)
        
        # 读取CSV文件
        entity_table = pd.read_csv(csv_file)
        entity_table["entity_name"] = entity_table["entity_name"].str.lower()
        
        # 将实体词汇添加到 all_entities 集合中
        all_entities.update(entity_table["entity_name"])

# 为实体词汇设置较高频率，确保它们在jieba分词时不被拆分
for entity in all_entities:
    jieba.add_word(entity, freq=1000)  # 设置一个较高的频率

# 自定义分词函数
def jieba_tokenizer(text):
    return [word for word in jieba.cut(text) if word not in stop_words]

# 使用中文分词 + bigram，添加实体词汇后计算 TF-IDF
vectorizer = TfidfVectorizer(
    tokenizer=jieba_tokenizer,    # 使用自定义的 jieba 分词器
    ngram_range=(1, 2),           # 识别一元和二元词组
    stop_words=None,              # 禁用默认的停用词         
)

# 重新计算 TF-IDF 矩阵
tfidf_matrix = vectorizer.fit_transform(document_contents.values())
feature_names = vectorizer.get_feature_names_out()

# 遍历文件夹中的所有CSV文件，计算实体的TF-IDF值
for filename in os.listdir(csv_folder):
    if filename.startswith('sample_entityTable_') and filename.endswith('.csv'):
        csv_file = os.path.join(csv_folder, filename)
        
        # 读取CSV文件
        entity_table = pd.read_csv(csv_file)
        entity_table["entity_name"] = entity_table["entity_name"].str.lower()

        # 重新计算每个实体的 TF-IDF 值
        for index, row in entity_table.iterrows():
            doc_title = row["document_title"]
            entity = row["entity_name"]  # 统一小写
            if doc_title in document_contents:
                # 直接获取文档的索引位置
                doc_idx = list(document_contents.keys()).index(doc_title)
                
                # 查找实体是否在特征中
                if entity in feature_names:
                    entity_idx = list(feature_names).index(entity)
                    tfidf_value = tfidf_matrix[doc_idx, entity_idx]
                    entity_table.at[index, "TF-IDF"] = tfidf_value
                else:
                    entity_table.at[index, "TF-IDF"] = 0  # 实体未出现在特征中
            else:
                entity_table.at[index, "TF-IDF"] = 0  # 文档未找到

        # 生成输出文件名
        output_filename = f"processed_{filename}"
        output_file = os.path.join(csv_folder, output_filename)
        
        # 将处理后的数据写回到新的CSV文件中
        entity_table.to_csv(output_file, index=False)

        print(f"数据处理完成，处理后的数据已保存到 {output_file}")