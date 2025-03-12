import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import glob
import os

# 定义一个函数，将嵌入向量字符串转换为numpy数组
def convert_to_array(embedding_str):
    embedding_list = embedding_str.strip('[]').split(',')
    return np.array(embedding_list, dtype=float)

# 定义一个函数，聚合嵌入向量
def aggregate_embeddings(group):
    embeddings = np.vstack(group).astype(float)
    embeddings = np.nan_to_num(embeddings)  # 将NaN值转换为0
    return np.mean(embeddings, axis=0)

# 读取文件夹中的所有CSV文件并合并为一个DataFrame
def read_and_merge(folder_path, column_name):
    all_data = []
    # 获取文件夹中所有CSV文件
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    for file in csv_files:
        df = pd.read_csv(file)
        df[column_name] = df[column_name].apply(convert_to_array)
        all_data.append(df)
    
    # 合并所有文件的数据
    return pd.concat(all_data, ignore_index=True)

# 指定文件夹路径
folder_path_1 = './数据表/entityTable_array'  # 存储 processed_entityTable_*.csv 的文件夹路径
folder_path_2 = './数据表/sample_entityTable_array'  # 存储 processed_sample_entityTable_*.csv 的文件夹路径

# 读取并合并第一个文件夹中的数据
merged_table1 = read_and_merge(folder_path_1, 'entity_description_embedding')
aggregated_table1 = merged_table1.groupby('document_title').apply(lambda x: aggregate_embeddings(x['entity_description_embedding'])).reset_index()
aggregated_table1 = aggregated_table1.rename(columns={0: 'aggregated_embedding_1'})

# 读取并合并第二个文件夹中的数据
merged_table2 = read_and_merge(folder_path_2, 'entity_description_embedding')
aggregated_table2 = merged_table2.groupby('document_title').apply(lambda x: aggregate_embeddings(x['entity_description_embedding'])).reset_index()
aggregated_table2 = aggregated_table2.rename(columns={0: 'aggregated_embedding_2'})

# 初始化结果列表
results = []

# 计算余弦相似度
for title1, embedding1 in aggregated_table1[['document_title', 'aggregated_embedding_1']].values:
    for title2, embedding2 in aggregated_table2[['document_title', 'aggregated_embedding_2']].values:
        sim = cosine_similarity([embedding1], [embedding2])[0][0]
        results.append((title1, title2, sim))

# 将结果列表转换为DataFrame
results_df = pd.DataFrame(results, columns=['DocumentTitle1', 'DocumentTitle2', 'CosineSimilarity'])

# 保存结果到CSV文件
results_df.to_csv('description_cosine_similarity_results.csv', index=False)

print("余弦相似度结果已保存到 'description_cosine_similarity_results.csv'")