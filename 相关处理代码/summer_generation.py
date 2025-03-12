import os
import glob
import dashscope
import csv

# 配置API信息（建议将密钥存储在环境变量中）
dashscope.api_key = "sk-5e722a2957874914b878051bdb37f7a4"  # 替换为你的API Key
model_name = "qwen2.5-72b-instruct"  # 使用qwen2.5-72b-instruct模型

def generate_summary(text):
    """
    使用通义千问生成文本摘要
    """
    try:
        response = dashscope.Generation.call(
            model=model_name,
            prompt=f"请为以下文本生成一个简洁的内容摘要，要求突出核心内容和关键信息：\n{text}",
            max_length=300,  # 最大输出长度
            top_p=0.8,  # 多样性控制
            temperature=0.7  # 创造性控制
        )
        return response.output.text
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return None

def process_documents(input_dir, output_csv):
    """
    处理目录中的文本文件，并将结果保存到CSV文件中
    """
    # 获取所有txt文件
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))

    # 打开CSV文件，准备写入
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["文件名", "摘要"])  # 写入表头

        for file_path in txt_files:
            try:
                # 读取文件内容
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 生成摘要
                print(f"正在处理文件: {os.path.basename(file_path)}")
                summary = generate_summary(content)

                if summary:
                    # 将结果写入CSV文件
                    csv_writer.writerow([os.path.basename(file_path), summary])
                    print(f"已生成摘要：{os.path.basename(file_path)}")
                else:
                    print(f"未能为 {file_path} 生成摘要")
                    csv_writer.writerow([os.path.basename(file_path), "生成摘要失败"])

            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                csv_writer.writerow([os.path.basename(file_path), f"处理出错: {str(e)}"])

if __name__ == "__main__":
    # 配置路径（根据实际情况修改）
    input_directory = "./二次拆分书稿数据集/"  # 原始文档目录
    output_csv_file = "summaries.csv"  # 输出CSV文件路径

    process_documents(input_directory, output_csv_file)
    print("处理完成！")