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

# 提取document_title和entity_name
titles_entities_table1 = merged_table1[['document_title', 'entity_name']].drop_duplicates()
titles_entities_table2 = merged_table2[['document_title', 'entity_name']].drop_duplicates()

# 创建一个空的DataFrame来存储结果
results = pd.DataFrame(columns=['DocumentTitle1', 'DocumentTitle2', 'CoOccurrenceCount'])

# 遍历表1中的每个document_title
for title1 in titles_entities_table1['document_title'].unique():
    # 遍历表2中的每个document_title
    for title2 in titles_entities_table2['document_title'].unique():
        # 获取两个表中对应document_title的entity_name集合
        entities1 = set(titles_entities_table1[titles_entities_table1['document_title'] == title1]['entity_name'])
        entities2 = set(titles_entities_table2[titles_entities_table2['document_title'] == title2]['entity_name'])

        # 计算共现的entity_name数量
        co_occurrence_count = len(entities1.intersection(entities2))

        # 如果有共现的entity_name，添加到结果DataFrame中
        
        new_row = pd.DataFrame(
            {'DocumentTitle1': [title1], 'DocumentTitle2': [title2], 'CoOccurrenceCount': [co_occurrence_count]})
        results = pd.concat([results, new_row], ignore_index=True)

# 保存结果到CSV文件
results.to_csv('document_title_co_occurrence.csv', index=False)

print("共线关系结果已保存到 'document_title_co_occurrence.csv'")