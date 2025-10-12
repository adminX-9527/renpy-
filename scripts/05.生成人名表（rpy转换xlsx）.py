import os
import re
from openpyxl import Workbook

def main():
    print("=== 游戏文本提取脚本启动 ===\n")

    # 1️⃣ 确定路径
    root_dir = os.getcwd()
    print(f"游戏根目录: {root_dir}")

    rpy_path = os.path.join(root_dir, "name.rpy")
    xlsx_path = os.path.join(root_dir, "name.xlsx")

    if not os.path.exists(rpy_path):
        print(f"❌ 找不到文件: {rpy_path}")
        input("\n按回车键关闭窗口...")
        return

    print(f"找到文件: {rpy_path}")

    # 2️⃣ 读取 rpy 文件内容
    with open(rpy_path, "r", encoding="utf-8") as f:
        content = f.read()
    print("✅ 文件读取完成")

    # 3️⃣ 提取 old / new 内容
    old_texts = re.findall(r'old\s+"([^"]+)"', content)
    new_texts = re.findall(r'new\s+"([^"]+)"', content)

    print(f"提取到 old 文本数: {len(old_texts)}")
    print(f"提取到 new 文本数: {len(new_texts)}")

    # 对齐长度
    max_len = max(len(old_texts), len(new_texts))
    old_texts += [""] * (max_len - len(old_texts))
    new_texts += [""] * (max_len - len(new_texts))

    # 4️⃣ 写入 Excel 文件
    wb = Workbook()
    ws = wb.active
    ws.title = "name提取结果"
    ws.append(["old", "new"])

    for o, n in zip(old_texts, new_texts):
        ws.append([o, n])

    wb.save(xlsx_path)
    print(f"✅ 数据已写入文件: {xlsx_path}")

    # 5️⃣ 手动关闭
    print("\n=== 任务完成 ===")
    input("按回车键关闭窗口...")

if __name__ == "__main__":
    main()
