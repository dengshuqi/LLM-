import pandas as pd
import os
import re

# 读取 CSV 文件
summaries_df = pd.read_csv("./数据表/summaries.csv")

# 初始化知识点列
summaries_df['knowledge'] = None

# 定义一个函数来提取知识点
def extract_knowledge(line):
    # 正则表达式匹配汉字数字加顿号，后跟任意空白字符和任意字符
    match = re.match(r'^([一二三四五六七八九十])、\s*(.*)', line)
    if match:
        return match.group(2).strip()  # 返回匹配的第二个分组（知识点）并去除两端空格
    return line.strip()  # 如果没有匹配，返回原始行并去除两端空格

# 遍历文件名列表，提取知识点
for index, row in summaries_df.iterrows():
    filename = row['文件名']
    txt_filename = os.path.join('./二次拆分书稿数据集/', filename)  # 构造 txt 文件名
    
    try:
        # 检查 txt 文件是否存在
        if os.path.exists(txt_filename):
            with open(txt_filename, 'r', encoding='utf-8') as file:
                first_line = file.readline().strip()  # 读取第一行并去除两端空格
                knowledge = extract_knowledge(first_line)  # 提取知识点
                summaries_df.at[index, 'knowledge'] = knowledge  # 存入知识点
        else:
            print(f"文件 {txt_filename} 不存在")
            summaries_df.at[index, 'knowledge'] = "文件不存在"
    except Exception as e:
        print(f"处理文件 {txt_filename} 时出错: {str(e)}")
        summaries_df.at[index, 'knowledge'] = f"处理出错: {str(e)}"

# 保存更新后的 DataFrame 到新的 CSV 文件
summaries_df.to_csv("updated_summaries.csv", index=False)