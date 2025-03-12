import os
import csv
from neo4j import GraphDatabase

def batch_export_data(uri, user, password, query, batch_size, output_dir):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    offset = 0
    batch_number = 1

    while True:
        paginated_query = f"""
        {query}
        SKIP {offset}
        LIMIT {batch_size}
        """
        with driver.session() as session:
            result = session.run(paginated_query)
            records = list(result)

        if not records:
            print("No more records to fetch. Export completed.")
            break

        # 将记录写入 CSV 文件
        file_name = f"batch_{batch_number}.csv"
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow([key for key in records[0].keys()])
            # 写入数据
            for record in records:
                writer.writerow(record.values())

        print(f"Exported batch {batch_number} to {file_path}")
        offset += batch_size
        batch_number += 1

    driver.close()

# 调用函数
uri = "neo4j+s://9976c605.databases.neo4j.io"
user = "neo4j"
password = "G0zfZE-RFkVU_HZu8hi9NKnEWLt3wenBydu6YD3t3hU"
query = """
MATCH (c:__Chunk__)-[:PART_OF]->(d:__Document__) 
MATCH (c)-[:HAS_ENTITY]->(e:__Entity__)
RETURN 
    d.id AS document_id,
    d.title AS document_title,
    e.id AS entity_id,
    e.name AS entity_name,
    e.type AS entity_type,
    e.description AS entity_description,
    e.description_embedding AS entity_description_embedding
"""
batch_size = 4000
output_dir = "output_csv"
os.makedirs(output_dir, exist_ok=True)

batch_export_data(uri, user, password, query, batch_size, output_dir)