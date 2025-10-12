import os

# --------------------------
# 1. 脚本所在目录即为游戏根目录
# --------------------------
root_dir = os.path.abspath(os.path.dirname(__file__))
game_dir = os.path.join(root_dir, "game")

# --------------------------
# 2. 遍历找到 game 目录下（包括子文件夹）的全部 rpyc 文件
# --------------------------
rpyc_files = []

for dirpath, dirnames, filenames in os.walk(game_dir):
    for file in filenames:
        if file.endswith(".rpyc"):
            rpyc_files.append(os.path.join(dirpath, file))

# --------------------------
# 3. 删除全部找到的 rpyc 文件
# --------------------------
if rpyc_files:
    print("开始删除 rpyc 文件：\n")
    for file_path in rpyc_files:
        try:
            os.remove(file_path)
            print(f"已删除: {file_path}")
        except Exception as e:
            print(f"删除失败: {file_path}，原因: {e}")
else:
    print("未找到任何 rpyc 文件。")

# --------------------------
# 4. 保持执行面板不关闭
# --------------------------
print("\n全部操作完成。")
input("请按回车键关闭此窗口...")
