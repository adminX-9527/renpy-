import os

# 1. 根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
schinese_dir = os.path.join(root_dir, "schinese")
result_file = os.path.join(root_dir, "result.txt")

# 2. 读取替换规则（支持空格或 Tab 分隔）
replace_rules = []
with open(result_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):  # 跳过空行或注释
            continue
        # 使用任意空白符分割（空格或 Tab）
        parts = line.split(None, 1)  # 只分割成两部分
        if len(parts) != 2:
            print(f"跳过格式不正确的行: {line}")
            continue
        replace_content, match_content = parts
        replace_rules.append((match_content, replace_content))

print(f"共读取 {len(replace_rules)} 条替换规则")

# 3. 遍历 schinese 目录下的所有 .rpy 文件
rpy_files = []
for root, dirs, files in os.walk(schinese_dir):
    for file in files:
        if file.endswith(".rpy"):
            rpy_files.append(os.path.join(root, file))

print(f"找到 {len(rpy_files)} 个 rpy 文件需要处理")

# 4. 逐文件处理
for rpy_file in rpy_files:
    print(f"\n处理文件: {rpy_file}")
    with open(rpy_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    for i, line in enumerate(lines, start=1):
        original_line = line
        for match_content, replace_content in replace_rules:
            if match_content in line:
                line = line.replace(match_content, replace_content)
                changed = True
                # 打印具体行号和内容变化
                print(f"行 {i}: '{match_content}' -> '{replace_content}'")
        new_lines.append(line)

    # 5. 保存文件
    if changed:
        with open(rpy_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"文件已保存: {rpy_file}")
    else:
        print("无内容需要替换，文件保持不变")

print("\n全部文件处理完成！")
input("按任意键关闭执行面板...")
