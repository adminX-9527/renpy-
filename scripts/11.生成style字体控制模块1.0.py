import os
import gzip
import base64
import re

def main():
    print("=== 游戏字体安装脚本 ===\n")

    game_root = os.path.abspath(os.path.dirname(__file__))
    print(f"[1] 游戏根目录: {game_root}")

    schinese_dir = os.path.join(game_root, "game", "tl", "schinese")
    os.makedirs(schinese_dir, exist_ok=True)
    print(f"[2] 确保目录存在: {schinese_dir}")

    style_rpy_path = os.path.join(schinese_dir, "style.rpy")
    style_rpy_content = '''translate schinese python:
    #游戏内对话文本字体
    gui.text_font = "tl/schinese/fonts/SourceHanSansCN-Bold.ttf"
    #游戏内人物角色名称字体
    gui.name_text_font = "tl/schinese/fonts/KNMaiyuan-Regular.ttf"
    #设置页面字体
    gui.interface_text_font = "tl/schinese/fonts/MiSans-Bold.ttf"
    #系统设置字体
    gui.button_text_font = gui.interface_text_font
    #游戏内选项文本字体
    gui.choice_button_text_font = gui.text_font
    #系统默认字体
    gui.system_font = "tl/schinese/fonts/MiSans-Regular.ttf"
'''
    with open(style_rpy_path, "w", encoding="utf-8") as f:
        f.write(style_rpy_content)
    print(f"[3] 已生成 style.rpy 文件: {style_rpy_path}")

    font_data_path = os.path.join(game_root, "font_data.py")
    if not os.path.exists(font_data_path):
        print(f"[!] 找不到 font_data.py 文件: {font_data_path}")
        return
    print(f"[4] 读取字体数据文件: {font_data_path}")

    # 读取文件内容
    with open(font_data_path, "r", encoding="utf-8") as f:
        font_data_code = f.read()

    # 使用正则提取 PACKED_FONTS
    pattern = re.compile(r'"([^"]+?)":\s*\(\s*"""(.*?)"""\s*\)', re.S)
    matches = pattern.findall(font_data_code)
    if not matches:
        print("[!] 没有匹配到字体数据")
        return

    packed_fonts = {name: data for name, data in matches}
    print(f"[4] 成功解析 PACKED_FONTS，共 {len(packed_fonts)} 个字体")

    fonts_dir = os.path.join(schinese_dir, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    print(f"[5] 确保字体目录存在: {fonts_dir}")

    # 解压字体
    for font_name, encoded_data in packed_fonts.items():
        try:
            print(f"[6] 正在处理字体: {font_name}")
            # 去掉换行和空格
            compressed_str = "".join(encoded_data.split())
            # base64 解码
            compressed_bytes = base64.b64decode(compressed_str)
            # gzip 解压
            font_bytes = gzip.decompress(compressed_bytes)
            # 写入文件
            font_path = os.path.join(fonts_dir, font_name)
            with open(font_path, "wb") as f:
                f.write(font_bytes)
            print(f"    -> 已解压字体到: {font_path}")
        except Exception as e:
            print(f"    [!] 解压失败: {e}")

    print("\n=== 完成！请手动关闭面板 ===")
    input("按 Enter 键退出...")

if __name__ == "__main__":
    main()