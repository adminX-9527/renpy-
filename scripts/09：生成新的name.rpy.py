# -*- coding: utf-8 -*-
import os
import re
import shutil

def main():
    print("=== 脚本开始执行 ===")

    # 1：确认当前目录为游戏根目录
    root_dir = os.getcwd()
    print(f"游戏根目录: {root_dir}")

    # 2：生成记忆池文件和 name.rpy、NameDele.txt
    memory_a = os.path.join(root_dir, "记忆池A.txt")
    memory_b = os.path.join(root_dir, "记忆池B.txt")
    memory_c = os.path.join(root_dir, "记忆池C.txt")
    name_rpy = os.path.join(root_dir, "name.rpy")
    name_dele = os.path.join(root_dir, "NameDele.txt")

    for f in [memory_a, memory_b, memory_c, name_rpy, name_dele]:
        if os.path.exists(f):
            os.remove(f)
    open(memory_a, "w", encoding="utf-8").close()
    open(memory_b, "w", encoding="utf-8").close()
    open(memory_c, "w", encoding="utf-8").close()
    open(name_rpy, "w", encoding="utf-8").close()
    open(name_dele, "w", encoding="utf-8").close()
    print("记忆池A/B/C、name.rpy、NameDele.txt 已创建。")

    # 3：处理 name.txt
    name_txt = os.path.join(root_dir, "name.txt")
    if not os.path.exists(name_txt):
        print("未找到 name.txt 文件，脚本终止。")
        return

    with open(name_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(memory_a, "w", encoding="utf-8") as a, open(name_dele, "a", encoding="utf-8") as dele:
        for line in lines:
            line = line.strip()
            # 排除包含 [] 或 {}
            if "[" in line or "]" in line or "{" in line or "}" in line:
                dele.write(line + "\n")
                continue
            # 排除非字母符号的行
            if re.search(r"[^A-Za-z\s\-]", line):
                dele.write(line + "\n")
                continue
            if line:
                a.write(line + "\n")

    print("已处理 name.txt 并写入 记忆池A 与 NameDele.txt。")

    # 4：提取 game/tl/schinese 目录内所有 .rpy 文件中的字符串
    target_dir = os.path.join(root_dir, "game", "tl", "schinese")
    rpy_files = []
    for dirpath, _, filenames in os.walk(target_dir):
        for f in filenames:
            if f.endswith(".rpy"):
                rpy_files.append(os.path.join(dirpath, f))

    pattern = r'"((?:\\.|[^"\\])*)"'

    with open(memory_b, "w", encoding="utf-8") as b:
        for file in rpy_files:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(pattern, content)
                for m in matches:
                    b.write(m.strip() + "\n")

    print(f"共提取 {len(rpy_files)} 个 rpy 文件内容到 记忆池B。")

    # 5：比较 记忆池A 与 记忆池B
    with open(memory_a, "r", encoding="utf-8") as a, open(memory_b, "r", encoding="utf-8") as b:
        lines_a = [l.strip() for l in a.readlines() if l.strip()]
        lines_b = set([l.strip() for l in b.readlines() if l.strip()])

    with open(memory_c, "w", encoding="utf-8") as c, open(name_dele, "a", encoding="utf-8") as dele:
        for line in lines_a:
            if line in lines_b:
                dele.write(line + "\n\n")  # 匹配内容写入 NameDele.txt 并空行
            else:
                c.write(line + "\n")

    print("记忆池A 与 记忆池B 对比完成，记忆池C 已生成。")

    # 6：将记忆池C内容写入 name.rpy
    with open(memory_c, "r", encoding="utf-8") as c:
        lines_c = [l.strip() for l in c.readlines() if l.strip()]

    with open(name_rpy, "w", encoding="utf-8") as n:
        n.write("translate schinese strings:\n")
        for line in lines_c:
            n.write(f'    old "{line}"\n')
            n.write('    new ""\n\n')

    print("name.rpy 文件已生成。")

    # 7：移动 name.rpy 到 game/tl/schinese 内
    dest_path = os.path.join(target_dir, "name.rpy")
    if os.path.exists(dest_path):
        os.remove(dest_path)
    shutil.move(name_rpy, dest_path)
    print(f"name.rpy 已移动到 {dest_path}")

    # 8：删除记忆池文件（此处已启用删除）
    for f in [memory_a, memory_b, memory_c]:
        try:
            os.remove(f)
            print(f"{os.path.basename(f)} 已删除。")
        except Exception as e:
            print(f"删除 {os.path.basename(f)} 时出错: {e}")

    print("=== 脚本执行完毕，窗口不会自动关闭 ===")
    input("按回车键退出...")

if __name__ == "__main__":
    main()
