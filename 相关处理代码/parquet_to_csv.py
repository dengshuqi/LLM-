import pandas as pd

# 读取 Parquet 文件
parquet_file = 'create_final_relationships.parquet'  # 替换为你的 Parquet 文件路径
df = pd.read_parquet(parquet_file)

# 保存为 CSV 文件
csv_file = 'create_final_relationships.csv'  # 替换为你想要保存的 CSV 文件路径
df.to_csv(csv_file, index=False)  # index=False 表示不将索引写入 CSV 文件