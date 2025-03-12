import os
import re


def split_sections(input_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历输入目录中的所有.txt文件
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 提取文件名中的基本信息
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split('_')

            # 确保文件名格式正确
            if len(parts) < 4:
                print(f"Skipping file {filename}: Incorrect format.")
                continue

            # 提取章节、小节、标题和书籍编号
            chapter = parts[0]
            section = parts[1]
            title = '_'.join(parts[2:-1])  # 合并可能拆分的标题部分
            book = parts[-1]
            book_number = book.split('_')[-1]

            # 使用修正后的正则表达式匹配每个小小节
            sections = re.split(r'\n*\n(?=[一二三四五六七八九十零]+、)', content)
            if len(sections) < 2:
                print(f"No sections found in file {filename}.")
                continue

            for i, section_content in enumerate(sections[1:], start=1):
                # 生成输出文件名
                output_filename = f"{chapter}_{section}_{title}_{book_number}.{i}.txt"
                output_path = os.path.join(output_dir, output_filename)

                # 写入输出文件
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(section_content.strip())

                print(f"Saved: {output_filename}")

    print("Processing complete.")


# 示例用法
input_directory = "./"  # 替换为你的输入目录路径
output_directory = "./slit/"  # 替换为你的输出目录路径
split_sections(input_directory, output_directory)