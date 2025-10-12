import openpyxl
import os
import sys

def process_game_data():
    """
    识别 'name.xlsx' 的第一列内容，并将其写入 'name.txt'。
    同时，将执行过程打印到控制台。
    """
    # 1: 脚本所在目录即为 游戏根目录
    # 确定游戏根目录（即脚本当前执行的目录）
    game_root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 构造 Excel 文件和 Text 文件的完整路径
    excel_file_path = os.path.join(game_root_dir, 'name.xlsx')
    text_file_path = os.path.join(game_root_dir, 'name.txt')
    
    # 打印流程信息
    print("-" * 50)
    print("--- 脚本执行开始 ---")
    print(f"1. 游戏根目录/当前工作目录: {game_root_dir}")
    print(f"2. 正在查找 Excel 文件: {excel_file_path}")
    
    # 检查 Excel 文件是否存在
    if not os.path.exists(excel_file_path):
        print(f"\n错误：未找到文件 {excel_file_path}。")
        print("请确保 'name.xlsx' 文件存在于游戏根目录下。")
        print("-" * 50)
        return

    try:
        # 3: 识别 游戏根目录\name.xlsx 文件
        # 加载 Excel 工作簿
        workbook = openpyxl.load_workbook(excel_file_path)
        # 默认选择第一个工作表
        sheet = workbook.active
        
        print("\n3. 成功加载 'name.xlsx' 文件。")
        print("   正在读取第一列（A列）的所有内容...")
        
        # 提取第一列（A列）的内容
        # row[0] 是获取该行中第一个单元格的值
        first_column_content = [str(row[0].value) for row in sheet.iter_rows(min_col=1, max_col=1) if row[0].value is not None]
        
        # 打印读取到的条目总数
        print(f"   共读取到 {len(first_column_content)} 条非空数据。")
        
        # 2: 在游戏根目录下生成一个 name.txt 文件
        # 3: 将第一列 全部内容，依次复制写入 name.txt 内
        with open(text_file_path, 'w', encoding='utf-8') as f:
            for item in first_column_content:
                f.write(item + '\n')
        
        print(f"\n4. 成功生成/覆盖文件: {text_file_path}")
        print("   第一列内容已全部写入 'name.txt' 文件中。")
        
        print("\n--- 脚本执行完毕 ---")
        print("-" * 50)

    except Exception as e:
        print(f"\n处理文件时发生错误: {e}")
        print("请检查 'name.xlsx' 文件是否损坏或被其他程序占用。")
        print("-" * 50)


# 4: 我需要看到在执行面板上看到执行的全部流程，执行面板不会自动关闭，需要手动关闭
if __name__ == "__main__":
    process_game_data()
    # 暂停执行，等待用户按下回车键，以保持执行面板开启
    input("\n流程已全部完成，请按回车键关闭窗口...")