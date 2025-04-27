import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox


def find_index_html_files(root_dir):
    """查找指定目录及其子目录下所有的 index.html 文件"""
    index_html_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower() == "index.html":
                full_path = os.path.join(root, file)
                index_html_files.append(full_path)
    return index_html_files


def merge_and_deduplicate_files(index_html_files, output_file):
    """合并所有 index.html 文件的内容，并去重"""
    unique_contents = set()  # 使用 set 来去重

    for file_path in index_html_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f_in:
                content = f_in.read()
                if content.strip():  # 检查内容非空
                    unique_contents.add(content)  # 使用 set 自动去重
                else:
                    print(f"Warning: {file_path} is empty or has only whitespace.")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if unique_contents:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for content in unique_contents:
                f_out.write(content + "\n\n")
        print(f"Unique contents have been saved to {output_file}")
    else:
        print("No content to write. Please check the input files.")


def remove_duplicate_characters(input_file, output_file):
    """从合并后的文件中去除重复字符，并保存结果"""
    try:
        unique_content = set()
        with open(input_file, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                unique_content.update(line)

        unique_content = "".join(sorted(unique_content, key=lambda x: line.index(x) if x in line else -1))

        if unique_content.strip():
            with open(output_file, 'w', encoding='utf-8') as f_out:
                f_out.write(unique_content)
            print(f"去重后的内容已保存到 {output_file}")
        else:
            print("去重后的内容为空，请检查输入文件内容。")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")


def compress_font(input_font_path, output_font_path, text_content):
    """压缩字体文件"""
    try:
        # 调用 pyftsubset 压缩字体
        cmd = ['pyftsubset', input_font_path, '--text=' + text_content, '--no-hinting',
               '--output-file=' + output_font_path]
        subprocess.run(cmd, check=True)
        print(f"字体已成功压缩并保存到 {output_font_path}")
    except Exception as e:
        print(f"压缩字体时发生错误: {e}")


def delete_unwanted_files(*files):
    """删除指定的文件"""
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            print(f"已删除文件: {file}")


# 图形化界面
app_data = {}


def on_select_index_dir():
    """选择包含index.html文件的目录"""
    dir_path = filedialog.askdirectory(title="选择包含index.html文件的目录")
    if dir_path:
        app_data['index_dir'] = dir_path
        dir_path_label.config(text=f"已选择目录: {dir_path}")


def on_select_font_file():
    """选择字体文件"""
    font_path = filedialog.askopenfilename(title="选择字体文件", filetypes=[("TrueType Fonts", "*.ttf")])
    if font_path:
        app_data['font_file'] = font_path
        font_path_label.config(text=f"已选择字体: {os.path.basename(font_path)}")


def on_process():
    """执行处理"""
    if 'index_dir' not in app_data or 'font_file' not in app_data:
        messagebox.showerror("错误", "请选择所有必需的文件和目录！")
        return

    index_dir = app_data['index_dir']
    font_file = app_data['font_file']

    # 禁用按钮，防止重复点击
    dir_select_button.config(state=tk.DISABLED)
    font_select_button.config(state=tk.DISABLED)
    process_button.config(state=tk.DISABLED)

    status_label.config(text="正在查找 index.html 文件...")

    # 临时文件路径
    merged_file = "output_unique.txt"
    deduplicated_file = "word.txt"

    # 步骤1：查找所有 index.html 文件
    print("正在查找 index.html 文件...")
    index_html_files = find_index_html_files(index_dir)

    # 步骤2：合并并去重文件内容
    if index_html_files:
        print("正在合并并去重以下 index.html 文件：")
        merge_and_deduplicate_files(index_html_files, merged_file)
    else:
        messagebox.showerror("错误", "未找到任何 index.html 文件")
        reset_ui()
        return

    # 步骤3：去除重复字符
    if os.path.exists(merged_file):
        print("正在去重字符...")
        remove_duplicate_characters(merged_file, deduplicated_file)

    # 步骤4：选择字体压缩
    if os.path.exists(deduplicated_file):
        with open(deduplicated_file, 'r', encoding='utf-8') as f:
            text_content = f.read()

        # 选择压缩字体
        output_font_path = "compressed_font.ttf"
        compress_font(font_file, output_font_path, text_content)

    # 步骤5：删除中间文件
    delete_unwanted_files(merged_file, deduplicated_file)

    # 更新状态并启用按钮
    status_label.config(text="操作完成！")
    messagebox.showinfo("完成", "文件处理已完成！")
    reset_ui()


def reset_ui():
    """恢复界面到初始状态"""
    dir_select_button.config(state=tk.NORMAL)
    font_select_button.config(state=tk.NORMAL)
    process_button.config(state=tk.NORMAL)


# 创建主窗口
root = tk.Tk()
root.title("博客字体压缩工具")
root.geometry("500x400")
root.config(bg="#F5F5F5")  # 背景色

# 设置标签和按钮的排版
frame = tk.Frame(root, bg="#F5F5F5")
frame.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)

# 选择index.html文件目录
dir_path_label = tk.Label(frame, text="请选择包含index.html文件的目录", wraplength=400, font=("Helvetica", 12),
                          bg="#F5F5F5", fg='#000')
dir_path_label.pack(pady=10)

dir_select_button = ttk.Button(frame, text="选择目录", command=on_select_index_dir)
dir_select_button.pack(pady=5, fill=tk.X)

# 选择字体文件
font_path_label = tk.Label(frame, text="请选择字体文件", wraplength=400, font=("Helvetica", 12), bg="#F5F5F5",
                           fg='#000')
font_path_label.pack(pady=10)

font_select_button = ttk.Button(frame, text="选择字体文件", command=on_select_font_file)
font_select_button.pack(pady=5, fill=tk.X)

# 状态标签
status_label = tk.Label(frame, text="准备开始任务", font=("Helvetica", 12), bg="#F5F5F5", fg='#000')
status_label.pack(pady=10)

# 执行按钮
process_button = ttk.Button(frame, text="开始处理", command=on_process)
process_button.config(style="TButton")
process_button.pack(pady=20, fill=tk.X)

# 自定义按钮样式
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10, relief="flat", background="#4CAF50", foreground="#000")

# 修改按钮在鼠标悬停时的效果
style.map("TButton", background=[("active", "#45a049")])

root.mainloop()
