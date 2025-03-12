from transformers import BertTokenizer, BertModel
import torch
import pandas as pd
import numpy as np
import re  # 导入正则表达式模块

# 加载预训练的BERT模型和分词器
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

# 读取数据
summaries = pd.read_csv('./数据表/sample_summaries.csv')  # 假设summaries表存储在summaries.csv文件中

# 预处理函数：去除无意义的符号和空格
def preprocess_text(text):
    if not isinstance(text, str):  # 如果不是字符串，直接返回空字符串
        return ""
    # 去除无意义的符号和多余的空格
    text = re.sub(r'\*+', '', text)  # 去除所有连续的*符号
    text = re.sub(r'\s+', ' ', text)  # 替换多个空格为一个空格
    text = text.strip()  # 去除首尾空格
    return text

# 对摘要字段进行预处理
summaries['摘要'] = summaries['摘要'].apply(preprocess_text)

# 定义获取BERT嵌入向量的函数
def get_bert_embedding(text):
    if not text:  # 如果文本为空，返回零向量
        return np.zeros(768)  # BERT的嵌入维度为768
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
    return cls_embedding

# 为每个预处理后的摘要生成BERT嵌入向量
summaries['摘要_embedding'] = summaries['摘要'].apply(get_bert_embedding)

# 将嵌入向量转换为字符串格式（便于保存为CSV）
summaries['摘要_embedding'] = summaries['摘要_embedding'].apply(lambda x: ','.join(map(str, x)))

# 保存为CSV文件，确保包含“文件名”这一列
summaries[['文件名', '摘要', '摘要_embedding']].to_csv('sample_summaries_embeddings.csv', index=False)

print("嵌入向量已保存到 'sample_summaries_embeddings.csv'")