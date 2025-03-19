import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

# 读取两个表
textEmbedding = pd.read_csv('./数据表/sample_combine_entity_extraction_embedding.csv')
knowledgeEmbedding = pd.read_csv('./数据表/combine_entity_extraction_embedding.csv')

# 打印列名，确认是否正确
print("textEmbedding columns:", textEmbedding.columns)
print("knowledgeEmbedding columns:", knowledgeEmbedding.columns)

# 定义一个函数，将嵌入向量字符串转换为numpy数组
def convert_to_array(embedding_str):
    try:
        # 如果是字符串格式的嵌入向量，去掉首尾的方括号并分割成列表
        embedding_list = embedding_str.strip('[]').split(',')
        embedding_array = np.array(embedding_list, dtype=float)
        return embedding_array
    except AttributeError:
        # 如果不是字符串（例如已经是numpy数组或其他类型），直接返回原值
        return embedding_str
    except Exception as e:
        # 捕获其他异常，并返回 None
        print(f"Error converting embedding: {embedding_str} - {e}")
        return None

# 将嵌入向量列转换为numpy数组
textEmbedding['摘要_embedding'] = textEmbedding['摘要_embedding'].apply(convert_to_array)
textEmbedding['aggregated_embedding'] = textEmbedding['aggregated_embedding'].apply(convert_to_array)

knowledgeEmbedding['摘要_embedding'] = knowledgeEmbedding['摘要_embedding'].apply(convert_to_array)
knowledgeEmbedding['aggregated_embedding'] = knowledgeEmbedding['aggregated_embedding'].apply(convert_to_array)

# 检查嵌入向量的维度是否一致
def check_embedding_dimension(embedding):
    if embedding is None or not isinstance(embedding, np.ndarray) or len(embedding) != 768:
        return False
    return True

# 过滤掉嵌入向量维度不正确的行
textEmbedding = textEmbedding[textEmbedding['摘要_embedding'].apply(check_embedding_dimension)]
textEmbedding = textEmbedding[textEmbedding['aggregated_embedding'].apply(check_embedding_dimension)]

knowledgeEmbedding = knowledgeEmbedding[knowledgeEmbedding['摘要_embedding'].apply(check_embedding_dimension)]
knowledgeEmbedding = knowledgeEmbedding[knowledgeEmbedding['aggregated_embedding'].apply(check_embedding_dimension)]

# 使用LSA对嵌入向量进行降维
def apply_lsa(embedding_matrix, n_components=100):
    svd = TruncatedSVD(n_components=n_components)
    reduced_matrix = svd.fit_transform(embedding_matrix)
    return reduced_matrix

# 将嵌入向量转换为矩阵
text_extraction_embeddings_matrix = np.vstack(textEmbedding['摘要_embedding'].dropna())
knowledge_extraction_embeddings_matrix = np.vstack(knowledgeEmbedding['摘要_embedding'].dropna())

text_aggregated_embeddings_matrix = np.vstack(textEmbedding['aggregated_embedding'].dropna())
knowledge_aggregated_embeddings_matrix = np.vstack(knowledgeEmbedding['aggregated_embedding'].dropna())

# 应用LSA降维
text_extraction_lsa = apply_lsa(text_extraction_embeddings_matrix)
knowledge_extraction_lsa = apply_lsa(knowledge_extraction_embeddings_matrix)

text_aggregated_lsa = apply_lsa(text_aggregated_embeddings_matrix)
knowledge_aggregated_lsa = apply_lsa(knowledge_aggregated_embeddings_matrix)

# 计算降维后的余弦相似度
cosine_sim_extraction = cosine_similarity(knowledge_extraction_lsa, text_extraction_lsa)
cosine_sim_aggregated = cosine_similarity(knowledge_aggregated_lsa, text_aggregated_lsa)

# 聚合两个表的嵌入向量（使用LSA降维后的向量）
knowledge_combined_embeddings_matrix = knowledge_extraction_lsa + knowledge_aggregated_lsa
text_combined_embeddings_matrix = text_extraction_lsa + text_aggregated_lsa

# 计算聚合后的余弦相似度
cosine_sim_combined = cosine_similarity(knowledge_combined_embeddings_matrix, text_combined_embeddings_matrix)

# 将余弦相似度矩阵转换为长格式的DataFrame
result_list = []
for i, title in enumerate(knowledgeEmbedding['文件名']):  # 文件名来自knowledgeEmbedding表
    for j, filename in enumerate(textEmbedding['文件名']):  # 文件名来自textEmbedding表
        sim_extraction = cosine_sim_extraction[i, j]
        sim_aggregated = cosine_sim_aggregated[i, j]
        sim_combined = cosine_sim_combined[i, j]
        result_list.append([title, filename, sim_extraction, sim_aggregated, sim_combined])

# 创建结果DataFrame
result_df = pd.DataFrame(result_list, columns=[
    'knowledge_title', '文件名',
    '摘要_embedding余弦相似度',
    'aggregated_embedding余弦相似度',
    '聚合后的余弦相似度'
])

# 保存为CSV文件
result_df.to_csv('cosine_similarity_results.csv', index=False)

print("余弦相似度结果已保存到 'cosine_similarity_results.csv'")