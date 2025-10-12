import os
import shutil

# 游戏根目录，脚本所在目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(ROOT_DIR, "game")

def log(msg):
    print(f"[INFO] {msg}")

def copy_file_to_root(src_filename):
    src_path = os.path.join(GAME_DIR, src_filename)
    dst_path = os.path.join(ROOT_DIR, src_filename)
    if not os.path.exists(src_path):
        log(f"源文件不存在: {src_path}")
        return None
    shutil.copy2(src_path, dst_path)
    log(f"已复制 {src_path} 到 {dst_path}")
    return dst_path

def read_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

def write_lines(filepath, lines):
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    log(f"已写入文件: {filepath}, 共 {len(lines)} 行")

def find_screen_preferences(lines):
    for i, line in enumerate(lines):
        if line.strip().startswith("screen preferences"):
            log(f"定位到 screen preferences, 行号: {i}")
            return i
    return None

def find_vbox_structure(lines, start_index):
    for i in range(start_index, len(lines)-1):
        line = lines[i]
        next_line = lines[i+1]
        if line.lstrip().startswith("vbox:") and \
           next_line.lstrip().startswith('style_prefix "check"'):
            log(f"找到代码结构A vbox, 行号: {i}")
            return i
    return None

def find_nearest_vbox(lines, start_index, end_index):
    for i in range(start_index+1, end_index):
        if lines[i].lstrip().startswith("vbox:"):
            log(f"找到最近 vbox 代码结构, 行号: {i}")
            return i
    return None

def insert_radio_code(lines, index_a, index_b):
    indent_b = len(lines[index_b]) - len(lines[index_b].lstrip())
    radio_code = [
        ' ' * indent_b + "vbox:\n",
        ' ' * (indent_b + 4) + 'style_prefix "radio"\n',
        ' ' * (indent_b + 4) + 'label ("Language")\n',
        ' ' * (indent_b + 4) + 'textbutton ("English") action Language(None)\n',
        ' ' * (indent_b + 4) + 'textbutton ("中文") text_font "tl/schinese/fonts/MiSans-Regular.ttf" action Language("schinese")\n'
    ]

    blank_line_index = None
    for i in range(index_a+1, index_b):
        if lines[i].strip() == "":
            blank_line_index = i
            log(f"在索引A与B之间找到空白行, 行号: {i}")
            break

    if blank_line_index is not None:
        lines.insert(blank_line_index, "\n")
        lines.insert(blank_line_index, "\n")
        for j, code_line in enumerate(radio_code):
            lines.insert(blank_line_index + 1 + j, code_line)
        log(f"在空白行下方插入radio代码, 插入起始行号: {blank_line_index+1}")
    else:
        for _ in range(3):
            lines.insert(index_b, "\n")
        for j, code_line in enumerate(radio_code):
            lines.insert(index_b + 1 + j, code_line)
        log(f"在索引B上方插入radio代码, 插入起始行号: {index_b+1}")

    return lines

def insert_language_define():
    options_path = copy_file_to_root("options.rpy")
    if options_path is None:
        log("options.rpy 文件复制失败，退出")
        return
    lines = read_lines(options_path)
    define_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("define config.name ="):
            define_index = i
            log(f"定位到 define config.name =, 行号: {i}")
            break
    if define_index is not None:
        insert_index = define_index + 1
        lines.insert(insert_index, '\n')
        lines.insert(insert_index + 1, 'define config.language = "schinese"\n')
        write_lines(options_path, lines)
        log(f"在 options.rpy 中插入 define config.language = 'schinese', 行号: {insert_index+1}")
    else:
        log("未找到 define config.name =，无法插入语言定义")

def main():
    log("脚本开始执行")
    screens_path = copy_file_to_root("screens.rpy")
    if screens_path is None:
        log("screens.rpy 文件复制失败，退出")
        return

    lines = read_lines(screens_path)
    screen_pref_index = find_screen_preferences(lines)
    if screen_pref_index is None:
        log("未找到 screen preferences，跳转步骤7")
        insert_language_define()
    else:
        index_a = find_vbox_structure(lines, screen_pref_index)
        if index_a is None:
            log("未找到代码结构A，删除 screens.rpy 并执行逻辑7")
            os.remove(screens_path)
            log("已删除根目录下 screens.rpy")
            insert_language_define()
        else:
            index_b = find_nearest_vbox(lines, index_a, len(lines))
            if index_b is None:
                index_b = index_a
                log("未找到索引B, 使用索引A作为参考")
            lines = insert_radio_code(lines, index_a, index_b)
            write_lines(screens_path, lines)
            log("操作完成，原始代码未修改，仅插入新代码")

    log("脚本执行完毕，手动关闭执行面板查看结果")
    input("按回车键退出...")

if __name__ == "__main__":
    main()
