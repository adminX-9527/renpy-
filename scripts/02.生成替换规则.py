import os
import re

# -------------------- 配置 --------------------
# 游戏根目录（脚本所在目录即为游戏根目录）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 输出文件路径
MEMORY_A_PATH = os.path.join(ROOT_DIR, "记忆池A.txt")
MEMORY_B_PATH = os.path.join(ROOT_DIR, "记忆池B.txt")
MEMORY_C_PATH = os.path.join(ROOT_DIR, "记忆池C.txt")
RESULT_PATH = os.path.join(ROOT_DIR, "result.txt")

# Emoji 列表
EMBEDDED_EMOJIS_DEDUPLICATED = [
    "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😇", "😈",
    "😉", "😊", "😋", "😌", "😍", "🥰", "😘", "😗", "😙", "😚",
    "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️",
    "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡",
    "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓",
    "🤔", "🤫", "🤭", "🤥", "😶", "😐", "😑", "😬", "😮‍💨", "😵",
    "😵‍💫", "😴", "🤤", "😮", "😲", "😎", "😛", "😜", "😝", "😪",
    "😷", "😸", "😹", "😺", "😻", "😼", "😽", "😾", "😿", "🙀",
    "🙂", "🙈", "🙉", "🙊", "🚣", "🚴", "🚵", "🚶", "🛀", "🛋️",
    "🛌", "🛍️", "🛎️", "🛏️", "🛒", "🤐", "🤑", "🤒", "🤕", "🤖",
    "🤗", "🤢", "🤧", "🤪", "🤮", "🥅", "🧓", "🧕", "⚽️", "🌀",
    "🌁", "🌂", "🌄", "🌅", "🌆", "🌇", "🌈", "🌉", "🌊", "🌌",
    "🌍", "🌎", "🌏", "🌐", "🌑", "🌒", "🌓", "🌔", "🌕", "🌖",
    "🌗", "🌘", "🌙", "🌚", "🌝", "🌞", "🌤️", "🌥️", "🌦️", "🌧️",
    "🌨️", "🌩️", "🌪️", "🌫️", "🌬️", "🌱", "🌲", "🌳", "🌴", "🌵",
    "🌷", "🌹", "🌺", "🌻", "🌼", "🌾", "🌿", "🍀", "🍁", "🍂",
    "🍃", "🍇", "🍉", "🍊", "🍋", "🍌", "🍎", "🍔", "🍕", "🍟",
    "🍦", "🍰", "🍷", "🍹", "🍺", "🎀", "🎁", "🎂", "🎈", "🎉",
    "🎊", "🎓", "🎙️", "🎤", "🎧", "🎨", "🎩", "🎭", "🎮", "🎯",
    "🎰", "🎱", "🎲", "🎳", "🎵", "🎶", "🎸", "🎹", "🎺", "🎻",
    "🎼", "🎽", "🎾", "🎿", "🏀", "🏁", "🏂", "🏃", "🏄", "🏅",
    "🏆", "🏇", "🏈", "🏉", "🏊", "🏋️", "🏐", "🏠", "🏡", "🏢",
    "🏥", "🏦", "🏪", "🏫", "🏬", "🏰", "🐱", "🐶", "👦", "👧",
    "👨", "👩", "👮", "👱", "👲", "👳", "👴", "👵", "👶", "👷",
    "👹", "👺", "👻", "👽", "👿", "💀", "💂", "💓", "💔", "💕",
    "💗", "💘", "💙", "💚", "💛", "💜", "💞", "🕴️", "📱", "📲",
    "☎", "📞", "📟", "📠", "🔋", "🔌", "💻", "💽", "💾", "💿",
    "📀", "🎥", "📺", "📷", "📹", "📼", "🔍", "🔎", "🔬", "🔭",
    "📡", "📔", "📕", "📖", "📗", "📘", "📙", "📚", "📓", "📃",
    "📜", "📄", "📰", "📑", "🔖", "💳", "✉", "📧", "📨", "📩",
    "📤", "📥", "📦", "📫", "📪", "📬", "📭", "📮", "✏", "✒",
    "📝", "📁", "📂", "📅", "📆", "📇", "📈", "📉", "📊", "📋",
    "📌", "📍", "📎", "📏", "📐", "✂", "🔒", "🔓", "🔏", "🔐",
    "🔑", "🚂", "🚃", "🚄", "🚅", "🚆", "🚇", "🚈", "🚉", "🚊",
    "🚝", "🚞", "🚋", "🚌", "🚍", "🚎", "🚏", "🚐", "🚑", "🚒",
    "🚓", "🚔", "🚕", "🚖", "🚗", "🚘", "🚚", "🚛", "🚜", "🚲",
    "⛽", "🚨", "🚥", "🚦", "🚧", "⚓", "⛵", "🚤", "🚢", "✈",
    "💺", "🚁", "🚟", "🚠", "🚡", "🚀", "🌋", "🏣", "🏤", "🏨",
    "🏩", "🏭", "🏯", "💒", "🗽", "⛪", "⛲", "🌃", "🎠", "🎡",
    "🎢", "🎑", "🗿", "🧍‍♀️", "🍈", "🍍", "🥭", "🍏", "🍐", "🍑",
    "🍒", "🍓", "🥝", "🍅", "🥥", "🥑", "🍆", "🥔", "🥕", "🌽",
    "🌶️", "🥒", "🥬", "🥦", "🧄", "🧅", "🍞", "🥐", "🥖", "🥨",
    "🥯", "🥞", "🧇", "🧀", "🍖", "🍗", "🥩", "🥓", "🌭", "🥪",
    "🌮", "🌯", "🥙", "🥚", "🍳", "🥘", "🍲", "🥣", "🍝", "🍜",
    "🍛", "🍣", "🍤", "🍥", "🍚", "🍘", "🍠", "🍡", "🍢", "🍨",
    "🍩", "🍪", "🧁", "🥧", "🍫", "🍬", "🍭", "🍮", "🍯", "🍼",
    "🥛", "☕", "🍵", "🍶", "🍾", "🥂", "🥃", "🧊", "🥄", "🍴",
    "🔪", "🥢", "🏖️", "🏜️", "🏝️", "🏞️", "🏟️", "🏗️", "🛣️", "🛤️",
    "🏙️", "🌁", "🛰️", "🛸", "⌚", "☎️", "⌨️", "🖱️", "🖲️", "💡",
    "🔦", "🕯️", "🗑️", "🛢️", "💸"
]

# -------------------- 步骤 1：遍历 rpy 文件并提取文本 --------------------
tl_dir = os.path.join(ROOT_DIR, "game", "tl", "schinese")
pattern = r'"((?:\\.|[^"\\])*)"'

memory_a_lines = []

print("开始遍历 rpy 文件...")
for root, dirs, files in os.walk(tl_dir):
    for file in files:
        if file.endswith(".rpy"):
            file_path = os.path.join(root, file)
            print(f"读取文件: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(pattern, content)
                for match in matches:
                    memory_a_lines.append(match)

# 写入记忆池A
with open(MEMORY_A_PATH, "w", encoding="utf-8") as f:
    for line in memory_a_lines:
        f.write(line + "\n")
print(f"记忆池A生成完成，{len(memory_a_lines)}条记录")

# -------------------- 步骤 2：识别 [[ 并写入记忆池B --------------------
memory_b_lines = []
for line in memory_a_lines:
    if "[[" in line:
        memory_b_lines.append(line)

with open(MEMORY_B_PATH, "w", encoding="utf-8") as f:
    for line in memory_b_lines:
        f.write(line + "\n")
print(f"记忆池B生成完成，{len(memory_b_lines)}条记录")

# -------------------- 步骤 3：提取 { } 和 [ ] 内内容写入记忆池C --------------------
memory_c_set = set()
for line in memory_a_lines:
    curly_matches = re.findall(r"\{.*?\}", line)
    square_matches = re.findall(r"\[.*?\]", line)
    for m in curly_matches + square_matches:
        memory_c_set.add(m)

memory_c_list = list(memory_c_set)
with open(MEMORY_C_PATH, "w", encoding="utf-8") as f:
    for item in memory_c_list:
        f.write(item + "\n")
print(f"记忆池C生成完成，{len(memory_c_list)}条记录")

# -------------------- 步骤 4：记忆池C 与 Emoji 配对写入 result.txt --------------------
result_lines = []
emoji_index = 0

for item in memory_c_list:
    if emoji_index < len(EMBEDDED_EMOJIS_DEDUPLICATED):
        emoji = EMBEDDED_EMOJIS_DEDUPLICATED[emoji_index]
        emoji_index += 1
        result_lines.append(f"{item}   {emoji}")
    else:
        print("Emoji 已用完，剩余内容无法配对")
        break

with open(RESULT_PATH, "w", encoding="utf-8") as f:
    for line in result_lines:
        f.write(line + "\n")
print(f"result.txt生成完成，共{len(result_lines)}条配对记录")

# -------------------- 步骤 5：删除记忆池文件（可注释） --------------------
os.remove(MEMORY_A_PATH)
os.remove(MEMORY_B_PATH)
os.remove(MEMORY_C_PATH)
print("记忆池文件已删除")

print("执行完成，脚本不会自动关闭，请手动关闭。")
input("按回车键退出...")
