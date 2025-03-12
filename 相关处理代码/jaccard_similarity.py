import pandas as pd
import glob
import os

# 定义一个函数，从文件夹中读取所有CSV文件并合并为一个DataFrame
def read_and_merge(folder_path):
    all_data = []
    # 获取文件夹中所有CSV文件
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    # 打印调试信息，确认是否找到文件
    print(f"Found {len(csv_files)} CSV files in folder '{folder_path}':")
    for file in csv_files:
        print(file)
        df = pd.read_csv(file)
        all_data.append(df)
    
    if not all_data:
        raise FileNotFoundError(f"No CSV files found in folder: {folder_path}")
    
    # 合并所有文件的数据
    return pd.concat(all_data, ignore_index=True)

# 指定文件夹路径
folder_path_1 = './数据表/entityTable_array'  # 存储 processed_entityTable_*.csv 的文件夹路径
folder_path_2 = './数据表/sample_entityTable_array'  # 存储 processed_sample_entityTable_*.csv 的文件夹路径

# 从文件夹中读取并合并数据
merged_table1 = read_and_merge(folder_path_1)
merged_table2 = read_and_merge(folder_path_2)

# 提取document_title和entity_name，并将entity_name转换为集合
entity_sets_table1 = merged_table1.groupby('document_title')['entity_name'].apply(set).reset_index(name='entity_names_1')
entity_sets_table2 = merged_table2.groupby('document_title')['entity_name'].apply(set).reset_index(name='entity_names_2')

# 定义计算Jaccard相似度的函数
def calculate_jaccard(set1, set2):
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0

# 初始化结果列表
results_list = []

# 遍历表1中的每个document_title的entity_name集合
for _, row1 in entity_sets_table1.iterrows():
    doc_title1 = row1['document_title']
    entities1 = row1['entity_names_1']
    # 遍历表2中的每个document_title的entity_name集合
    for _, row2 in entity_sets_table2.iterrows():
        doc_title2 = row2['document_title']
        entities2 = row2['entity_names_2']
        # 计算Jaccard相似度
        jaccard_sim = calculate_jaccard(entities1, entities2)
        # 将结果添加到列表中
        results_list.append({'DocumentTitle1': doc_title1, 'DocumentTitle2': doc_title2, 'JaccardSimilarity': jaccard_sim})

# 将结果列表转换为DataFrame
results = pd.DataFrame(results_list)

# 保存结果到CSV文件
results.to_csv('jaccard_similarity_results.csv', index=False)

print("Jaccard相似度结果已保存到 'jaccard_similarity_results.csv'")