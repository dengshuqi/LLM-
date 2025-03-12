import os
import glob
import requests
import csv

# 配置API信息
DEEPSEEK_API_KEY = "sk-dda6b2fe5c6f45919737d0b51f8fcd71"  # 请替换为你的真实API密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"

def generate_summary(text):
    """
    使用DeepSeek生成文本摘要
    """
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL_NAME,
            "messages": [{
                "role": "user",
                "content": f"请为以下文本生成一个简洁的内容摘要，要求突出核心内容和关键信息：\n{text}"
            }],
            "temperature": 0.7,
            "top_p": 0.8,
            "max_tokens": 300
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return None

# 修复点：补全函数实现代码
def process_documents(input_dir, output_csv):
    """
    处理目录中的文本文件，并将结果保存到CSV文件中
    """
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["文件名", "摘要"])

        for file_path in txt_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                print(f"正在处理文件: {os.path.basename(file_path)}")
                summary = generate_summary(content)

                if summary:
                    csv_writer.writerow([os.path.basename(file_path), summary])
                    print(f"已生成摘要：{os.path.basename(file_path)}")
                else:
                    print(f"未能为 {file_path} 生成摘要")
                    csv_writer.writerow([os.path.basename(file_path), "生成摘要失败"])

            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                csv_writer.writerow([os.path.basename(file_path), f"处理出错: {str(e)}"])

if __name__ == "__main__":
    input_directory = "./博客案例集/"
    output_csv_file = "sample_summaries.csv"

    process_documents(input_directory, output_csv_file)
    print("处理完成！")