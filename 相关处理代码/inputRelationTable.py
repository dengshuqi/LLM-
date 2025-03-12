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
MATCH (e1:__Entity__)-[r:RELATED]->(e2:__Entity__)
RETURN 
    e1.id AS entity_id_1,
    e1.name AS name_1,
    e1.type AS type_1,
    e2.id AS entity_id_2,
    e2.name AS name_2,
    e2.type AS type_2,
    r.id AS relation_id,
    r.human_readable_id AS human_readable_id,
    collect(r.text_unit_ids) AS text_unit_ids,
    r.description AS description,
    r.rank AS rank,
    r.weight AS weight
"""
batch_size = 4000
output_dir = "output1_csv"
os.makedirs(output_dir, exist_ok=True)

batch_export_data(uri, user, password, query, batch_size, output_dir)