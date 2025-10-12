import os
import re
import traceback
from pathlib import Path
import sys

# --- 配置 ---
# 脚本根目录即为游戏根目录
PROJECT_ROOT = Path(__file__).parent 

# 记忆池文件名
POOL_A = PROJECT_ROOT / "记忆池A.txt"
POOL_B = PROJECT_ROOT / "记忆池B.txt"
POOL_C = PROJECT_ROOT / "记忆池C.txt"
POOL_D = PROJECT_ROOT / "记忆池D.txt"
POOL_E = PROJECT_ROOT / "记忆池E.txt"
NAME_DELE = PROJECT_ROOT / "NameDele.txt"
TRANSLATE_RPY = PROJECT_ROOT / "translate.rpy"

# 目标搜索目录
GAME_DIR = PROJECT_ROOT / "game"
TL_S_CHINESE_DIR = PROJECT_ROOT / "game" / "tl" / "schinese"

# --- 核心函数：规则1: rpy文件字符串提取 ---
def extract_rpy_strings(file_path):
    """
    从 .rpy 文件中提取四类字符串：人名, 文本, 变量, 替换。
    返回格式：[人名列表, 文本列表, 变量列表, 替换列表]
    每个列表元素格式：(string, relative_path, line_number)
    """
    name_strings, text_strings, variable_strings, replace_strings = [], [], [], []
    relative_path = str(file_path.relative_to(PROJECT_ROOT))
    
    try:
        print(f"    -> 正在读取文件: {relative_path}")
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            lines = content.split('\n')

            # 1. 人名提取 (Character)
            char_patterns = [
                r'Character\s*\(\s*(["\'])((?:\\\1|.)*?)\1', 
                r'define\s+\w+\s*=\s*Character\s*\(\s*(["\'])((?:\\\1|.)*?)\1'
            ]
            for pattern in char_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_number = content.count('\n', 0, match.start()) + 1
                    string = match.group(2)
                    start_pos, line_start = match.start(), content.rfind('\n', 0, match.start())
                    # 排除 _() 包裹的字符串
                    if '_(' not in content[line_start if line_start != -1 else 0:start_pos]: 
                        name_strings.append((string, relative_path, line_number))

            # 2. 文本提取
            text_patterns = [
                r'\btext\s+(["\'])((?:\\\1|.)*?)\1\s*:', 
                r'\b(text|textbutton|show\s+text)\s+(["\'])((?:\\\2|.)*?)\2', 
                r'renpy\.input\s*\(\s*(["\'])((?:\\\1|.)*?)\1'
            ]
            for pattern in text_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    # 根据模式选择正确的捕获组
                    string_group_index = 3 if pattern == text_patterns[1] else 2
                    line_number = content.count('\n', 0, match.start()) + 1
                    string = match.group(string_group_index)
                    start_pos, line_start = match.start(), content.rfind('\n', 0, match.start())
                    # 排除 _() 包裹的字符串
                    if not re.search(r'_\s*\(\s*$', content[line_start if line_start != -1 else 0:start_pos].strip()): 
                        text_strings.append((string, relative_path, line_number))

            # 3. 变量/赋值提取
            variable_keywords = [r'default\s+\w+\s*=\s*', r'define\s+\w+\s*=\s*', r'\$\s*\w+\s*=\s*']
            for i, line in enumerate(lines):
                line_number = i + 1
                
                # 检查关键字和排除 _() 包裹的字符串
                for keyword in variable_keywords:
                    if re.search(keyword, line) and "Character" not in line and "renpy.input" not in line and not re.search(keyword + r'\s*_\s*\(', line):
                        for match in re.finditer(r'(["\'])((?:\\\1|.)*?)\1', line): 
                            variable_strings.append((match.group(2), relative_path, line_number))
                            
                # 检查普通赋值 (排除 define/default/$/image/transform/style/screen/menu)
                if re.match(r'^[a-zA-Z_]\w*\s*=\s*f?["\']', line.lstrip()) and not re.match(r'^(default|define|\$|image|transform|style|screen|menu)', line.lstrip()) and not re.search(r'=\s*_\s*\(', line):
                    for match in re.finditer(r'f?(["\'])((?:\\\1|.)*?)\1', line): 
                        variable_strings.append((match.group(2), relative_path, line_number))

            # 4. 替换字符串提取 (tooltip, call with string, notify/csay/message etc.)
            for i, line in enumerate(lines):
                line_number = i + 1
                
                # tooltip
                if 'tooltip' in line and not re.search(r'_\s*\(\s*tooltip', line):
                    for match in re.finditer(r'\btooltip\s*\(\s*(["\'])((?:\\\1|.)*?)\1', line): 
                        replace_strings.append((match.group(2), relative_path, line_number))
                
                # call ... from (字符串)
                if re.search(r'^\s*call\s+.*\s+from\b', line):
                    for match in re.finditer(r'(["\'])((?:\\\1|.)*?)\1', line):
                        if not re.search(r'_\s*\(\s*$', line[:match.start()].rstrip()): 
                            text_strings.append((match.group(2), relative_path, line_number))
                
                # notify/csay/Stream*
                if any(re.search(p, line) for p in [
                    r'^\s*\$\s*csay\s*\(', r'^\s*\$\s*renpy\.notify\s*\(', 
                    r'^\s*show\s+screen\s+my_notify\s*\(', r'^\s*\$\s*(StreamAdd|MessageCommit|StreamUpdate)\s*\('
                ]):
                    for match in re.finditer(r'(["\'])((?:\\\1|.)*?)\1', line):
                        if not re.search(r'_\s*\(\s*$', line[:match.start()].rstrip()): 
                            text_strings.append((match.group(2), relative_path, line_number))
                
                # call screen/message_start with string argument (首字母大写)
                if re.search(r'^\s*call\s+screen\s+\w+\s*\(', line) or re.search(r'^\s*call\s+message_start\s*\(', line):
                    if (args_match := re.search(r'\((.*)\)', line)):
                        for match in re.finditer(r'(["\'])((?:\\\1|.)*?)\1', args_match.group(1)):
                            string = match.group(2)
                            if string and string.strip() and string.strip()[0].isupper(): 
                                text_strings.append((string, relative_path, line_number))
                                replace_strings.append((string, relative_path, line_number))
                                
            # 5. ChoiceOption
            for match in re.finditer(r'ChoiceOption\s*\(\s*(["\'])((?:\\\1|.)*?)\1', content, re.IGNORECASE):
                line_number, start_pos = content.count('\n', 0, match.start()) + 1, match.start()
                context_start = content.rfind('ChoiceOption', 0, start_pos)
                if not re.search(r'_\s*\(\s*$', content[content.rfind('\n', 0, context_start)+1 : context_start].strip()): 
                    text_strings.append((match.group(2), relative_path, line_number))

    except Exception as e: 
        print(f"    !!! 错误：处理文件 {file_path} 时出错: {e}")
        traceback.print_exc()

    # 去除内部重复并合并所有列表
    all_strings = list(dict.fromkeys(name_strings + text_strings + variable_strings + replace_strings))
    return [all_strings, [], [], []] # 简化返回，只返回所有提取到的，以满足需求3的提取内容写入 C

# --- 核心函数：规则4: 统一字符串过滤 ---
def shared_filter_strings(strings_with_info):
    """
    统一的字符串过滤函数。
    (strings_with_info 格式: [(string, file_path, line_number), ...])
    """
    print("\n[步骤4] 正在执行统一字符串筛选...")
    filtered_list, deleted_list = [], []
    # 规则2: 文件扩展名
    file_extensions = ('.mp3', '.png', '.jpg', '.jpeg', '.ogg', '.wav', '.webp', '.gif', '.avi', '.mp4', '.mov', '.webm', '.flv', '.wmv', '.rpy')
    
    for string_info in strings_with_info:
        string = string_info[0]
        
        # 规则1: 空字符串/空格
        if not string or string.strip() == '':
            deleted_list.append((string_info, "R1: Empty/Space"))
            continue
            
        # 规则2: 文件路径/资源
        # 检查是否包含文件扩展名且没有空格（避免误删文件名或句子中的单词）
        if any(ext in string.lower() for ext in file_extensions) and ' ' not in string:
            deleted_list.append((string_info, "R2: File Path"))
            continue
            
        # 规则3: 非字母字符串 (去除标签后检查)
        temp_string = re.sub(r'\{.*?\}', '', string) # 去除 {标签}
        temp_string = re.sub(r'\[.*?\]', '', temp_string) # 去除 [变量]
        if not re.search(r'[a-zA-Z]', temp_string):
            deleted_list.append((string_info, "R3: No Letters"))
            continue
            
        # 规则4: 纯标签/方括号 (排除包含空格或{/的复杂标签)
        if (string.startswith('[') and string.endswith(']')) or (string.startswith('{') and string.endswith('}')):
            if '{/' not in string and ' ' not in string and not re.search(r'[\u4e00-\u9fa5]', string): # 排除中文标签
                deleted_list.append((string_info, "R4: Pure Tag"))
                continue
                
        # 规则5: 注释行
        if string.lstrip().startswith('#'):
            deleted_list.append((string_info, "R5: Comment"))
            continue
            
        # 规则6: 纯小写/非大写 (必须包含至少一个大写字母)
        # 修正：过滤掉不包含任何大写字母的字符串 (保持原意)
        if not any(char.isupper() for char in string):
            deleted_list.append((string_info, "R6: No Uppercase"))
            continue
            
        filtered_list.append(string_info)
    
    print(f"    筛选完成。原始: {len(strings_with_info)} 条, 过滤后: {len(filtered_list)} 条, 移除: {len(deleted_list)} 条。")
    return filtered_list, [item[0] for item in deleted_list] # 仅返回被删除的字符串信息

# --- 辅助函数：规则5: 写入记忆池A ---
def copy_first_column_d_to_a():
    """
    读取 记忆池D.txt，将第一列依次写入 记忆池A.txt。
    第一列保持原样，不做任何修改。
    """
    print("\n[步骤5] 正在将记忆池D的第一列写入记忆池A...")
    first_column_lines = []
    
    # 确保文件存在
    if not POOL_D.exists():
        print(f"    !!! 错误：文件 {POOL_D} 不存在，跳过步骤5。")
        return

    # 读取记忆池D
    try:
        with open(POOL_D, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip("\n")
                if line.strip() == "":
                    continue
                # 按制表符或空格分列，取第一列
                # 这里假设 D 文件是 制表符 分隔的 (string, file_path, line_number)
                first_col = line.split("\t", 1)[0]
                first_column_lines.append(first_col)
    except Exception as e:
        print(f"    !!! 错误：读取 {POOL_D} 时出错: {e}")
        return

    # 写入记忆池A
    try:
        with open(POOL_A, 'w', encoding='utf-8') as f:
            for item in first_column_lines:
                f.write(f"{item}\n")
        print(f"    已将 {len(first_column_lines)} 条内容写入 {POOL_A}。")
    except Exception as e:
        print(f"    !!! 错误：写入 {POOL_A} 时出错: {e}")

# --- 主执行流程 ---
def main():
    print("--- Ren'Py 额外文本提取与翻译辅助脚本 V1.0 ---")
    print(f"项目根目录: {PROJECT_ROOT}\n")

    # 步骤 2: 生成文件（如果不存在）并清空内容
    print("[步骤2] 正在创建/清空记忆池文件和辅助文件...")
    for f in [POOL_A, POOL_B, POOL_C, POOL_D, POOL_E, NAME_DELE, TRANSLATE_RPY]:
        try:
            with open(f, 'w', encoding='utf-8') as fp:
                if f == TRANSLATE_RPY:
                    # 步骤 8: 写入 translate.rpy 的起始内容
                    fp.write('translate schinese strings:\n')
                pass
            print(f"    已创建/清空: {f.name}")
        except Exception as e:
            print(f"    !!! 错误：创建/清空文件 {f.name} 失败: {e}")
            sys.exit(1)
    
    # 步骤 3: 遍历 game 文件夹并提取内容写入 记忆池C
    print("\n[步骤3] 正在遍历 game 文件夹并提取rpy文件中的字符串写入记忆池C...")
    all_extracted_strings = []
    game_path = PROJECT_ROOT / "game"
    
    if not game_path.exists():
        print(f"    !!! 错误：游戏根目录下的 'game' 文件夹不存在: {game_path}")
        print("    请检查脚本位置是否正确（应在游戏根目录）。")
        return

    for path in game_path.rglob('*.rpy'):
        # 排除 tl 文件夹内的所有文件
        if 'tl' not in path.parts:
            extracted = extract_rpy_strings(path)
            # extracted[0] 包含所有提取到的字符串信息 [(string, relative_path, line_number)]
            all_extracted_strings.extend(extracted[0])

    # 去除内部重复并写入 记忆池C
    unique_c_strings = list(dict.fromkeys(all_extracted_strings))
    try:
        with open(POOL_C, 'w', encoding='utf-8') as f:
            for string, file_path, line_number in unique_c_strings:
                # 写入格式: string\tfile_path\tline_number
                f.write(f"{string}\t{file_path}\t{line_number}\n")
        print(f"    所有提取到的 {len(unique_c_strings)} 条内容已写入 {POOL_C}。")
    except Exception as e:
        print(f"    !!! 错误：写入 {POOL_C} 时出错: {e}")

    # 步骤 4: 筛选 记忆池C 的内容，去重后写入 记忆池D
    filtered_d_strings, _ = shared_filter_strings(unique_c_strings)
    
    # 再次去重 (基于字符串内容)
    d_content_map = {}
    for string, file_path, line_number in filtered_d_strings:
        if string not in d_content_map:
            d_content_map[string] = (string, file_path, line_number)
    
    unique_d_strings = list(d_content_map.values())
    
    try:
        with open(POOL_D, 'w', encoding='utf-8') as f:
            for string, file_path, line_number in unique_d_strings:
                f.write(f"{string}\t{file_path}\t{line_number}\n")
        print(f"    筛选和二次去重后，{len(unique_d_strings)} 条内容已写入 {POOL_D}。")
    except Exception as e:
        print(f"    !!! 错误：写入 {POOL_D} 时出错: {e}")
        
    # 步骤 5: 将 记忆池D 的第一列写入 记忆池A
    copy_first_column_d_to_a()

    # 步骤 6: 遍历 tl/schinese 文件夹提取内容写入 记忆池B
    print("\n[步骤6] 正在遍历 tl/schinese 文件夹提取字符串写入记忆池B...")
    tl_schinese_path = PROJECT_ROOT / "game" / "tl" / "schinese"
    extracted_tl_strings = set()
    
    if not tl_schinese_path.exists():
        print(f"    警告：翻译文件夹不存在: {tl_schinese_path}，记忆池B将为空。")
    else:
        for path in tl_schinese_path.rglob('*.rpy'):
            try:
                print(f"    -> 正在读取翻译文件: {path.relative_to(PROJECT_ROOT)}")
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    # 严格使用规则: "((?:\\.|[^"\\])*)" 提取双引号内的内容
                    for match in re.finditer(r'"((?:\\.|[^"\\])*)"', content):
                        extracted_tl_strings.add(match.group(1))
            except Exception as e:
                print(f"    !!! 错误：读取翻译文件 {path} 时出错: {e}")

    try:
        with open(POOL_B, 'w', encoding='utf-8') as f:
            for item in extracted_tl_strings:
                f.write(f"{item}\n")
        print(f"    已从 tl/schinese 提取 {len(extracted_tl_strings)} 条内容并写入 {POOL_B}。")
    except Exception as e:
        print(f"    !!! 错误：写入 {POOL_B} 时出错: {e}")

    # 步骤 7: 匹配 记忆池A 和 记忆池B，结果写入 NameDele.txt 和 记忆池E
    print("\n[步骤7] 正在进行记忆池A和B的匹配和分离...")
    try:
        with open(POOL_A, "r", encoding="utf-8") as a:
            lines_A = [l.strip() for l in a.readlines() if l.strip()]
    except FileNotFoundError:
        print(f"    !!! 错误：文件 {POOL_A} 不存在，跳过步骤7。")
        return
    
    try:
        with open(POOL_B, "r", encoding="utf-8") as b:
            # 使用 set 进行快速查找
            lines_B = set([l.strip() for l in b.readlines() if l.strip()])
    except FileNotFoundError:
        print(f"    警告：文件 {POOL_B} 不存在，所有内容将写入 {POOL_E}。")
        lines_B = set()

    matched_count = 0
    unmatched_count = 0
    unmatched_lines = []
    
    try:
        with open(POOL_E, "w", encoding="utf-8") as pool_e, open(NAME_DELE, "a", encoding="utf-8") as dele:
            for line in lines_A:
                if line in lines_B:
                    dele.write(line + "\n\n") # 匹配内容写入 NameDele.txt 并空行
                    matched_count += 1
                else:
                    unmatched_lines.append(line)
                    pool_e.write(line + "\n") # 不能匹配的内容写入 记忆池E
                    unmatched_count += 1
                    
        # 步骤 7 要求将不能匹配的内容放入记忆池E，并覆盖/重写 记忆池A (这块逻辑与原代码片段有冲突，
        # 原代码片段是写回 POOL_A，但要求是写入 POOL_E。我们遵循最终目标：写入 E。)
        # 补充：根据原始要求，未匹配的内容应该被写入记忆池E，因此不再写回记忆池A。

        print(f"    匹配完成：匹配到 {matched_count} 条，未匹配 {unmatched_count} 条。")
        print(f"    - 匹配内容已追加到 {NAME_DELE.name}")
        print(f"    - 未匹配内容已写入 {POOL_E.name}")
        
    except Exception as e:
        print(f"    !!! 错误：在步骤7中处理文件时出错: {e}")

    # 步骤 9: 遍历 记忆池E 写入 translate.rpy
    print("\n[步骤9] 正在将记忆池E的内容格式化写入 translate.rpy...")
    try:
        # 再次读取记忆池E (因为上面步骤7已经写入了)
        with open(POOL_E, "r", encoding="utf-8") as f:
            e_lines = [l.strip() for l in f.readlines() if l.strip()]
            
        with open(TRANSLATE_RPY, "a", encoding="utf-8") as f:
            for line in e_lines:
                # 格式: old "行内容" \n new ""
                # 需要对行内容中的引号进行转义
                safe_line = line.replace('\\', '\\\\').replace('"', '\\"')
                f.write(f'\n    old "{safe_line}"\n    new ""\n')
        
        print(f"    已将 {len(e_lines)} 条内容格式化追加到 {TRANSLATE_RPY}。")
    except Exception as e:
        print(f"    !!! 错误：在步骤9中处理文件时出错: {e}")


    # 步骤 10: 清理文件
    print("\n[步骤10] 正在清理临时文件...")
    files_to_delete = [POOL_A, POOL_B, POOL_C, POOL_D, POOL_E, NAME_DELE]
    deleted_count = 0
    for f in files_to_delete:
        try:
            if f.exists():
                f.unlink()
                print(f"    - 已删除: {f.name}")
                deleted_count += 1
        except Exception as e:
            print(f"    !!! 警告：删除文件 {f.name} 失败: {e}")
            
    print(f"    共清理了 {deleted_count} 个临时文件。")
    
    print("\n--- 脚本执行完毕 ---")
    input("请按任意键关闭窗口...") # 确保执行面板不会自动关闭

if __name__ == "__main__":
    main()