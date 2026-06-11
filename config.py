"""全局配置常量"""

# ── 计时时长（秒） ──
WORK_DURATION = 25 * 60       # 25 分钟
SHORT_BREAK_DURATION = 5 * 60 # 5 分钟
LONG_BREAK_DURATION = 15 * 60 # 15 分钟
POMODOROS_PER_CYCLE = 4       # 每 4 个番茄后进入长休息

# ── UI 尺寸 ──
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 560
PROGRESS_RING_SIZE = 280      # 圆环直径
PROGRESS_RING_WIDTH = 14      # 圆环线宽

# ── 颜色主题 ──
# 暖棕黑底，番茄红 + 鼠尾草绿 + 灰蓝，灵感来自手工厨房计时器
COLOR_BG = "#1a1412"               # 深暖棕黑背景
COLOR_FRAME_BG = "#221b17"         # 卡片/面板背景
COLOR_TEXT = "#e8ddd5"             # 暖白主文字
COLOR_TEXT_SECONDARY = "#9a8e84"   # 暖灰次要文字
COLOR_ACCENT_WORK = "#e0554a"      # 番茄红 — 工作
COLOR_ACCENT_SHORT_BREAK = "#7d9b76"  # 鼠尾草绿 — 短休息
COLOR_ACCENT_LONG_BREAK = "#5a8db5"   # 灰蓝 — 长休息
COLOR_BUTTON = "#3d302b"           # 暖棕按钮背景
COLOR_BUTTON_HOVER = "#5a463d"     # 按钮悬停
COLOR_BUTTON_TEXT = "#e8ddd5"      # 按钮文字
COLOR_RING_TRACK = "#2a1f1b"       # 暖灰轨道（比背景稍亮）
COLOR_RING_GLOW = "#3a1f18"        # 光晕底色
COLOR_TOGGLE_ON = "#e0554a"        # 开关开启 — 番茄红
COLOR_TOGGLE_OFF = "#4a3d36"       # 开关关闭
COLOR_DOT_PATTERN = "#1f1815"      # 背景网点
COLOR_PAUSE = "#c9a96e"            # 暂停 — 暖金色
COLOR_IDLE_RING = "#3d302b"        # 空闲圆环色

# ── 字体 ──
FONT_TIMER = ("Microsoft YaHei", 52, "bold")
FONT_LABEL = ("Microsoft YaHei", 13)
FONT_BUTTON = ("Microsoft YaHei", 14)
FONT_SMALL = ("Microsoft YaHei", 11)
FONT_COUNTER = ("Microsoft YaHei", 12, "bold")
FONT_TITLE = ("Microsoft YaHei", 18, "bold")

# ── 中文字符串 ──
STR_APP_TITLE = "番茄钟"
STR_PHASE_IDLE = "准备开始"
STR_PHASE_WORK = "专注"
STR_PHASE_SHORT_BREAK = "小憩"
STR_PHASE_LONG_BREAK = "长休息"
STR_PHASE_PAUSED = "已暂停"
STR_START = "开始专注"
STR_PAUSE = "暂停"
STR_RESUME = "继续"
STR_RESET = "重置"
STR_SKIP = "跳过"
STR_ALWAYS_ON_TOP = "窗口置顶"
STR_SOUND = "提示音"
STR_TODAY_COUNT = "今日番茄"
STR_NOTIFICATION_WORK_DONE = "工作时间结束！休息一下吧 🍅"
STR_NOTIFICATION_BREAK_DONE = "休息时间结束！继续加油 💪"
STR_TRAY_SHOW = "显示窗口"
STR_TRAY_QUIT = "退出"
STR_TOOLTIP = "番茄钟"

# ── 持久化 ──
APP_DATA_DIR_NAME = "pomodoro_timer"
SESSION_FILE_NAME = "sessions.json"
