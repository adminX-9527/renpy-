import os
import re
import sys
from pathlib import Path

# --- 常量定义 ---
# 游戏根目录即为脚本所在目录
GAME_ROOT = Path(__file__).resolve().parent

# 记忆池文件名
POOL_A = GAME_ROOT / "记忆池A.txt"
POOL_B = GAME_ROOT / "记忆池B.txt"
POOL_C = GAME_ROOT / "记忆池C.txt"
POOL_D = GAME_ROOT / "记忆池D.txt"
POOL_E = GAME_ROOT / "记忆池E.txt"
POOL_F = GAME_ROOT / "记忆池F.txt"

# 其他文件
NAME_DELE = GAME_ROOT / "NameDele.txt"
NAME_TXT = GAME_ROOT / "name.txt"
NAME_RPY = GAME_ROOT / "name.rpy"

# 定义符A
DEFINER_A = "\n----------------截断---------------\n"

# 日志输出函数
def log(message):
    print(f"[LOG] {message}")

# --- 核心逻辑函数 ---

# 步骤 1 & 2: 初始化和文件生成
def step_1_and_2():
    log("步骤 1 & 2: 检查/创建工作目录和文件...")
    
    # 步骤 2: 在游戏根目录生成文件
    for f in [POOL_A, POOL_B, POOL_C, POOL_D, POOL_E, POOL_F, NAME_DELE, NAME_TXT]:
        try:
            f.touch(exist_ok=True)
            # 清空NameDele.txt 和 name.txt，其他后面逻辑会覆盖
            if f in [NAME_DELE, NAME_TXT]:
                with open(f, "w", encoding="utf-8") as file:
                    file.write("") 
            log(f"  - 文件 {f.name} 确保存在并已准备好。")
        except Exception as e:
            log(f"  - 错误: 无法创建或访问文件 {f.name}: {e}")
            sys.exit(1)

    # 步骤 2: 生成 定义符A
    # 定义符A内容已在DEFINER_A常量中定义，并将在步骤5, 6中使用。
    log("  - 定义符A 已定义。")

    log("步骤 1 & 2 完成。")
    print("-" * 50)

# 步骤 3: 遍历并提取 define 变量名 = 内容到 记忆池A
def step_3():
    log("步骤 3: 遍历 game 目录并提取 'define 变量名 =' 内容到 记忆池A...")
    
    game_dir = GAME_ROOT / "game"
    tl_dir = game_dir / "tl"
    
    if not game_dir.is_dir():
        log(f"  - 错误: 游戏根目录缺少 'game' 文件夹。请确保脚本在游戏根目录运行。")
        return
        
    all_defines = []
    
    # 查找 game 及其子文件夹内的全部 rpy 文件
    rpy_files = [p for p in game_dir.rglob("*.rpy")]
    
    # 排除 game/tl 内的 rpy 文件
    valid_rpy_files = [p for p in rpy_files if not str(p).startswith(str(tl_dir))]

    # 正则表达式匹配 'define 变量名 =' 及其整行内容
    # 严格匹配行首的 'define' 关键字
    define_pattern = re.compile(r"^\s*define\s+[\w\d]+\s*=\s*.*$", re.MULTILINE)

    for rpy_file in valid_rpy_files:
        try:
            with open(rpy_file, "r", encoding="utf-8") as f:
                content = f.read()
                matches = define_pattern.findall(content)
                if matches:
                    all_defines.extend(matches)
                    log(f"  - 从 {rpy_file.relative_to(GAME_ROOT)} 提取到 {len(matches)} 行 'define' 内容。")
        except UnicodeDecodeError:
            log(f"  - 警告: 无法以 utf-8 读取文件 {rpy_file.name}，跳过。")
        except Exception as e:
            log(f"  - 错误: 读取文件 {rpy_file.name} 发生未知错误: {e}")
            
    # 写入 记忆池A
    try:
        with open(POOL_A, "w", encoding="utf-8") as f:
            for line in all_defines:
                f.write(line.strip() + "\n")
        log(f"  - 成功将 {len(all_defines)} 行内容写入 记忆池A.txt。")
    except Exception as e:
        log(f"  - 错误: 写入 记忆池A.txt 失败: {e}")

    log("步骤 3 完成。")
    print("-" * 50)

# 步骤 4 & 4.2: 提取角色名到 记忆池B
def step_4():
    log("步骤 4 & 4.2: 从 记忆池A 提取角色名到 记忆池B...")
    
    extracted_names = []
    
    try:
        with open(POOL_A, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        log("  - 错误: 记忆池A.txt 未找到。请检查步骤3是否成功执行。")
        return

    # 步骤 4 正则: define 变量名 = Character('角色名'[, 角色属性=值, ...])
    # 匹配 Character 构造函数中的第一个字符串参数
    pattern_char = re.compile(r"=\s*Character\s*\(\s*['\"]([^'\"]+)['\"]") 
    
    # 步骤 4.2 正则: define 变量名 = '角色名'
    # 匹配整个定义右侧只是一个字符串字面量的情况
    pattern_str = re.compile(r"=\s*['\"]([^'\"]+)['\"]\s*$")

    for line in lines:
        line = line.strip()
        
        # 优先匹配 步骤 4
        match_char = pattern_char.search(line)
        if match_char:
            name = match_char.group(1).strip()
            if name:
                extracted_names.append(name)
                # log(f"  - 匹配 Character 提取: '{name}'")
            continue # 如果匹配到 Character，则不继续匹配 4.2

        # 匹配 步骤 4.2
        match_str = pattern_str.search(line)
        if match_str:
            name = match_str.group(1).strip()
            if name:
                extracted_names.append(name)
                # log(f"  - 匹配 纯字符串 提取: '{name}'")
    
    # 写入 记忆池B (不覆盖已有内容，但由于前面是空的，实际是写入)
    try:
        with open(POOL_B, "w", encoding="utf-8") as f:
            for name in extracted_names:
                f.write(name + "\n")
        log(f"  - 成功提取 {len(extracted_names)} 个角色名到 记忆池B.txt。")
    except Exception as e:
        log(f"  - 错误: 写入 记忆池B.txt 失败: {e}")

    log("步骤 4 & 4.2 完成。")
    print("-" * 50)

# 步骤 5 & 5.5: 去重、剪切、写入 NameDele、复制到 记忆池C
def step_5_and_5_5():
    log("步骤 5 & 5.5: 记忆池B 去重、分类和复制到 记忆池C...")

    try:
        with open(POOL_B, "r", encoding="utf-8") as f:
            lines_B = [l.strip() for l in f.readlines()]
    except FileNotFoundError:
        log("  - 错误: 记忆池B.txt 未找到。")
        return

    # 步骤 5: 去重处理
    unique_lines_B = list(set([line for line in lines_B if line])) # 去重并排除空行
    log(f"  - 记忆池B 去重后剩余 {len(unique_lines_B)} 个非空行。")

    # 用于存放将被保留在 记忆池B 中的行
    lines_to_keep_in_B = unique_lines_B.copy()
    deleted_to_namedele = []

    # 5.1 剪切 开头不是字母 的行
    # re.match 确保是从行首开始匹配
    non_alpha_start = [line for line in lines_to_keep_in_B if not re.match(r"^[a-zA-Z]", line)]
    lines_to_keep_in_B = [line for line in lines_to_keep_in_B if re.match(r"^[a-zA-Z]", line)]
    deleted_to_namedele.extend(non_alpha_start)
    log(f"  - 剪切 {len(non_alpha_start)} 行 (开头不是字母) 到 NameDele.txt。")

    # 5.2 再次剪切 首字母不是大写 的行
    non_upper_start = [line for line in lines_to_keep_in_B if not re.match(r"^[A-Z]", line)]
    lines_to_keep_in_B = [line for line in lines_to_keep_in_B if re.match(r"^[A-Z]", line)]
    deleted_to_namedele.extend(non_upper_start)
    log(f"  - 再次剪切 {len(non_upper_start)} 行 (首字母不是大写) 到 NameDele.txt。")

    # 写入 NameDele (不删除已有的内容；在内容最下方写入 定义符A)
    try:
        with open(NAME_DELE, "a", encoding="utf-8") as f:
            for line in deleted_to_namedele:
                f.write(line + "\n")
            f.write(DEFINER_A)
        log(f"  - 成功将 {len(deleted_to_namedele)} 行内容追加写入 NameDele.txt 并写入 定义符A。")
    except Exception as e:
        log(f"  - 错误: 写入 NameDele.txt 失败: {e}")

    # 将保留的行写回 记忆池B (实现“剪切”效果)
    try:
        with open(POOL_B, "w", encoding="utf-8") as f:
            for line in lines_to_keep_in_B:
                f.write(line + "\n")
        log(f"  - 记忆池B 更新为保留的 {len(lines_to_keep_in_B)} 行内容。")
    except Exception as e:
        log(f"  - 错误: 更新 记忆池B.txt 失败: {e}")

    # 步骤 5.5: 遍历读取 记忆池B,排除空行后复制写入 记忆池C
    # 由于 lines_to_keep_in_B 已经是去重且非空的，直接使用
    try:
        with open(POOL_C, "w", encoding="utf-8") as f:
            for line in lines_to_keep_in_B:
                f.write(line + "\n")
        log(f"  - 成功将 {len(lines_to_keep_in_B)} 行内容复制写入 记忆池C.txt。")
    except Exception as e:
        log(f"  - 错误: 写入 记忆池C.txt 失败: {e}")

    log("步骤 5 & 5.5 完成。")
    print("-" * 50)


# 步骤 6: 记忆池C 过滤和分流
def step_6():
    log("步骤 6: 记忆池C 过滤、分流到 NameDele.txt 和 name.txt/记忆池D...")
    
    try:
        with open(POOL_C, "r", encoding="utf-8") as f:
            lines_C = [l.strip() for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        log("  - 错误: 记忆池C.txt 未找到。")
        return

    # 规则: [\(\)\{\}\[\]\d\\\/#!]
    # 包含任何括号、数字、反斜杠、正斜杠、井号、感叹号的行
    filter_pattern = re.compile(r"[\(\)\{\}\[\]\d\\\/#!]")
    
    to_namedele_from_C = []
    to_name_txt_and_D = []
    
    for line in lines_C:
        if filter_pattern.search(line):
            to_namedele_from_C.append(line)
        else:
            to_name_txt_and_D.append(line)

    # 写入 NameDele (不删除已有的内容；在内容最下方写入 定义符A)
    try:
        with open(NAME_DELE, "a", encoding="utf-8") as f:
            for line in to_namedele_from_C:
                f.write(line + "\n")
            f.write(DEFINER_A)
        log(f"  - 成功将 {len(to_namedele_from_C)} 行(符合过滤规则)追加写入 NameDele.txt 并写入 定义符A。")
    except Exception as e:
        log(f"  - 错误: 写入 NameDele.txt 失败: {e}")
        
    # 写入 name.txt 与 记忆池D
    try:
        with open(NAME_TXT, "w", encoding="utf-8") as f_name, open(POOL_D, "w", encoding="utf-8") as f_d:
            for line in to_name_txt_and_D:
                f_name.write(line + "\n")
                f_d.write(line + "\n")
        log(f"  - 成功将 {len(to_name_txt_and_D)} 行内容写入 name.txt 和 记忆池D.txt。")
    except Exception as e:
        log(f"  - 错误: 写入 name.txt 或 记忆池D.txt 失败: {e}")

    log("步骤 6 完成。")
    print("-" * 50)

# 步骤 7: 遍历 game/tl/schinese 提取字符串到 记忆池E
def step_7():
    log("步骤 7: 遍历 game/tl/schinese 提取字符串到 记忆池E...")
    
    schinese_dir = GAME_ROOT / "game" / "tl" / "schinese"
    
    if not schinese_dir.is_dir():
        log(f"  - 错误: 缺少 'game/tl/schinese' 文件夹。")
        return
        
    all_strings = set() # 使用 set 暂存，避免重复

    # 查找 schinese 及其子文件夹内的全部 rpy 文件
    rpy_files = schinese_dir.rglob("*.rpy")
    
    # 严格使用规则: "((?:\\.|[^"\\])*)" 提取内容
    # 这个正则匹配双引号内的所有内容 (包括转义字符)
    string_pattern = re.compile(r'"((?:\\.|[^"\\])*)"')

    for rpy_file in rpy_files:
        try:
            with open(rpy_file, "r", encoding="utf-8") as f:
                content = f.read()
                # 查找所有匹配的双引号字符串
                matches = string_pattern.findall(content)
                if matches:
                    # 将提取到的内容加入集合
                    for match in matches:
                        # 仅保留非空字符串
                        if match.strip():
                            all_strings.add(match)
                    log(f"  - 从 {rpy_file.relative_to(GAME_ROOT)} 提取到 {len(matches)} 个字符串内容。")
        except UnicodeDecodeError:
            log(f"  - 警告: 无法以 utf-8 读取文件 {rpy_file.name}，跳过。")
        except Exception as e:
            log(f"  - 错误: 读取文件 {rpy_file.name} 发生未知错误: {e}")
            
    # 写入 记忆池E
    all_strings_list = list(all_strings)
    try:
        with open(POOL_E, "w", encoding="utf-8") as f:
            for s in all_strings_list:
                f.write(s + "\n")
        log(f"  - 成功将 {len(all_strings_list)} 个去重后的字符串内容写入 记忆池E.txt。")
    except Exception as e:
        log(f"  - 错误: 写入 记忆池E.txt 失败: {e}")

    log("步骤 7 完成。")
    print("-" * 50)

# 步骤 8: 记忆池D 和 记忆池E 匹配与分流
def step_8():
    log("步骤 8: 记忆池D 和 记忆池E 匹配与分流...")
    
    # 读取 记忆池D 和 记忆池 E
    try:
        with open(POOL_D, "r", encoding="utf-8") as a, open(POOL_E, "r", encoding="utf-8") as b:
            # 严格按照用户提供的代码逻辑读取
            lines_D = [l.strip() for l in a.readlines() if l.strip()]
            lines_E = set([l.strip() for l in b.readlines() if l.strip()])
    except FileNotFoundError as e:
        log(f"  - 错误: 读取 记忆池D.txt 或 记忆池E.txt 失败: {e}")
        return

    # 准备写入 NameDele.txt 和 记忆池F.txt
    
    # 用户提供的代码逻辑：将 NameDele.txt 作为 'dele'，将 记忆池D.txt 作为 'c' (待写入 记忆池F 的内容)
    # 这段代码逻辑实际是将匹配的内容写入 NameDele.txt, 将不匹配的内容 **写回** 记忆池D。
    # 为了遵循 “不能匹配的内容依次放入 记忆池F” 的要求，我需要修改用户提供的代码的 **写入逻辑**，
    # 但保留其 **读取和判断逻辑**。
    
    # 内存中执行判断
    matched_lines = []
    unmatched_lines_to_F = []
    
    for line in lines_D:
        # 匹配: 整行全部一样，包括字母，符号，括号，空格等等
        # 由于 lines_D 和 lines_E 都是 strip() 过的，这里的 line in lines_E 
        # 实现了整行完全匹配（不考虑首尾空白）
        if line in lines_E:
            matched_lines.append(line)
        else:
            unmatched_lines_to_F.append(line)
            
    # 写入 NameDele.txt
    try:
        with open(NAME_DELE, "a", encoding="utf-8") as dele:
            for line in matched_lines:
                dele.write(line + "\n\n")  # 匹配内容写入 NameDele.txt 并空行
        log(f"  - 成功将 {len(matched_lines)} 行匹配内容追加写入 NameDele.txt (含空行)。")
    except Exception as e:
        log(f"  - 错误: 写入 NameDele.txt 失败: {e}")
        
    # 写入 记忆池F
    try:
        with open(POOL_F, "w", encoding="utf-8") as f:
            for line in unmatched_lines_to_F:
                f.write(line + "\n")
        log(f"  - 成功将 {len(unmatched_lines_to_F)} 行不匹配内容写入 记忆池F.txt。")
    except Exception as e:
        log(f"  - 错误: 写入 记忆池F.txt 失败: {e}")

    # 清空 记忆池D (因为其内容已经分流完毕)
    try:
        with open(POOL_D, "w", encoding="utf-8") as f:
            f.write("")
        log("  - 记忆池D.txt 已清空。")
    except Exception as e:
        log(f"  - 错误: 清空 记忆池D.txt 失败: {e}")


    log("步骤 8 完成。")
    print("-" * 50)

# 步骤 9: 格式化 记忆池F 内容到 name.rpy 并删除记忆池
def step_9_and_cleanup():
    log("步骤 9: 格式化 记忆池F 内容到 name.rpy...")
    
    try:
        with open(POOL_F, "r", encoding="utf-8") as f:
            lines_F = [l.strip() for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        log("  - 错误: 记忆池F.txt 未找到。")
        lines_F = []
        
    if not lines_F:
        log("  - 记忆池F.txt 内容为空，name.rpy 不会生成内容。")
        
    rpy_content = ['translate schinese strings:']
    for line in lines_F:
        # 使用 repr() 处理可能包含引号的字符串，确保输出到 rpy 时引号正确
        rpy_content.append(f'    old "{line.replace("\\", "\\\\").replace("\"", "\\\"")}"')
        rpy_content.append(f'    new ""')
        rpy_content.append("") # 插入空行以分隔

    # 写入 name.rpy
    try:
        with open(NAME_RPY, "w", encoding="utf-8") as f:
            f.write("\n".join(rpy_content).strip() + "\n")
        log(f"  - 成功将 {len(lines_F)} 行内容转换为 Ren'Py 格式并写入 name.rpy。")
    except Exception as e:
        log(f"  - 错误: 写入 name.rpy 失败: {e}")
        
    log("步骤 9 完成。")
    
    # 步骤 10: 删除记忆池A、B、C、D、E、F
    log("步骤 10: 执行清理操作，删除记忆池文件...")
    pools_to_delete = [POOL_A, POOL_B, POOL_C, POOL_D, POOL_E, POOL_F]
    deleted_count = 0
    for p in pools_to_delete:
        try:
            if p.exists():
                p.unlink()
                log(f"  - 已删除 {p.name}。")
                deleted_count += 1
        except Exception as e:
            log(f"  - 警告: 无法删除文件 {p.name}: {e}")
            
    log(f"  - 总共删除了 {deleted_count} 个记忆池文件。")
    print("-" * 50)


# --- 主执行逻辑 ---
def main():
    print("=" * 50)
    print("            Ren'Py 角色名提取与分流工具")
    print("=" * 50)
    
    try:
        step_1_and_2()
        step_3()
        step_4()
        step_5_and_5_5()
        step_6()
        step_7()
        step_8()
        step_9_and_cleanup()
    except Exception as e:
        log(f"脚本执行过程中发生严重错误: {e}")
        
    print("=" * 50)
    print("所有步骤执行完毕。")
    print("=" * 50)

    # 步骤 10: 执行面板不会自动消失，需要手动关闭
    input("请按任意键关闭此窗口...")

if __name__ == "__main__":
    main()