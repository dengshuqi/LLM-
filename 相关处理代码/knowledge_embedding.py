from transformers import BertTokenizer, BertModel
import torch
import pandas as pd
import numpy as np
import glob
import os

# 加载预训练的BERT模型和分词器
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

# 定义一个函数，从文件夹中读取所有CSV文件并合并为一个DataFrame
def read_and_merge(folder_path):
    all_data = []
    # 获取文件夹中所有CSV文件
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in folder: {folder_path}")
    
    for file in csv_files:
        df = pd.read_csv(file)
        all_data.append(df)
    
    # 合并所有文件的数据
    return pd.concat(all_data, ignore_index=True)

# 读取并合并文件夹中的所有数据
folder_path = './数据表/sample_entityTable_array'  # 存储 processed_entityTable_*.csv 的文件夹路径
all_data = read_and_merge(folder_path)

# 获取BERT嵌入向量的函数
def get_bert_embedding(text):
    if not isinstance(text, str) or not text.strip():
        return np.zeros(768)  # 如果文本为空，返回零向量
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
    return cls_embedding

# 为每个entity_name生成嵌入向量
all_data['entity_name_embedding'] = all_data['entity_name'].apply(get_bert_embedding)

# 定义聚合函数
def aggregate_embeddings(group):
    embeddings = np.stack(group['entity_name_embedding'].values)
    avg_embedding = np.mean(embeddings, axis=0)
    return avg_embedding

# 按document_title分组并聚合嵌入向量
grouped = all_data.groupby('document_title').apply(aggregate_embeddings).reset_index(name='aggregated_embedding')

# 将嵌入向量转换为字符串格式
grouped['aggregated_embedding'] = grouped['aggregated_embedding'].apply(lambda x: ','.join(map(str, x)))

# 保存为CSV文件
grouped.to_csv('aggregated_sample_entity_embeddings.csv', index=False)
print("输出完成")