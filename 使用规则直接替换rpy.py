import os
import shutil

def main():
    print("=== 🎮 RPY 文件处理脚本开始执行 ===\n")

    # 1️⃣ 确定根目录
    root_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"【1】根目录路径：{root_dir}")

    # 2️⃣ 创建 schinese 文件夹（如果不存在）
    schinese_dir = os.path.join(root_dir, "schinese")
    if not os.path.exists(schinese_dir):
        os.makedirs(schinese_dir)
        print(f"【2】已创建目录：{schinese_dir}")
    else:
        print(f"【2】目录已存在：{schinese_dir}")

    # 3️⃣ 遍历读取 game/tl/schinese 下的 rpy 文件并复制到 schinese
    src_dir = os.path.join(root_dir, "game", "tl", "schinese")
    if not os.path.exists(src_dir):
        print(f"❌ 未找到源路径：{src_dir}")
        return

    print(f"\n【3】开始复制文件：{src_dir} → {schinese_dir}")
    for file_name in os.listdir(src_dir):
        if file_name.endswith(".rpy"):
            src_file = os.path.join(src_dir, file_name)
            dst_file = os.path.join(schinese_dir, file_name)
            shutil.copy2(src_file, dst_file)
            print(f"✅ 已复制：{file_name}")
    print("🎯 所有 rpy 文件复制完成。\n")

    # 4️⃣ 读取 result.txt 规则
    result_file = os.path.join(root_dir, "result.txt")
    if not os.path.exists(result_file):
        print(f"❌ 未找到规则文件：{result_file}")
        return

    print("【4】开始读取替换规则：")
    replace_rules = []
    with open(result_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                parts = line.split("  ")  # 尝试双空格分割
            if len(parts) < 2:
                parts = line.split(" ")   # 尝试单空格分割
            if len(parts) >= 2:
                key = parts[0].strip()
                value = parts[-1].strip()
                replace_rules.append((key, value))
                print(f"   🔁 规则：'{key}' → '{value}'")

    if not replace_rules:
        print("⚠️ 未读取到任何替换规则，请检查 result.txt 格式。")
        return

    print("\n【5】开始处理 schinese 文件夹内的 rpy 文件内容：")
    for file_name in os.listdir(schinese_dir):
        if not file_name.endswith(".rpy"):
            continue
        file_path = os.path.join(schinese_dir, file_name)
        print(f"➡️ 正在处理：{file_name}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 应用所有替换规则
        for old, new in replace_rules:
            if old in content:
                count = content.count(old)
                content = content.replace(old, new)
                print(f"   ✳️ 替换 {count} 次：'{old}' → '{new}'")

        # 保存修改后的文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"💾 已保存修改：{file_name}\n")

    print("✅ 所有替换操作完成！")
    print("\n=== 🎉 任务执行完毕 ===")
    input("按回车键关闭执行面板...")

if __name__ == "__main__":
    main()
