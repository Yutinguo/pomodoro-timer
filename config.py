"""全局配置常量"""

# ── 计时时长（秒） ──
WORK_DURATION = 25 * 60       # 25 分钟
SHORT_BREAK_DURATION = 5 * 60 # 5 分钟
LONG_BREAK_DURATION = 15 * 60 # 15 分钟
POMODOROS_PER_CYCLE = 4       # 每 4 个番茄后进入长休息

# ── UI 尺寸 ──
WINDOW_WIDTH = 380
WINDOW_HEIGHT = 480
PROGRESS_RING_SIZE = 260      # 圆环直径
PROGRESS_RING_WIDTH = 12      # 圆环线宽

# ── 颜色主题 ──
COLOR_BG = "#2b2b2b"               # 深色背景（匹配 CTk 暗色主题）
COLOR_FRAME_BG = "#16213e"         # 卡片/面板背景
COLOR_TEXT = "#e0e0e0"             # 主文字
COLOR_TEXT_SECONDARY = "#a0a0a0"   # 次要文字
COLOR_ACCENT_WORK = "#e94560"      # 工作 — 红色
COLOR_ACCENT_SHORT_BREAK = "#4caf84"  # 短休息 — 绿色
COLOR_ACCENT_LONG_BREAK = "#4a9eff"   # 长休息 — 蓝色
COLOR_BUTTON = "#0f3460"           # 按钮背景
COLOR_BUTTON_HOVER = "#1a4a7a"     # 按钮悬停
COLOR_BUTTON_TEXT = "#ffffff"      # 按钮文字
COLOR_RING_TRACK = "#2a2a4a"       # 圆环背景轨道
COLOR_TOGGLE_ON = "#e94560"        # 开关开启
COLOR_TOGGLE_OFF = "#4a4a6a"       # 开关关闭

# ── 字体 ──
FONT_TIMER = ("Microsoft YaHei", 48, "bold")
FONT_LABEL = ("Microsoft YaHei", 14)
FONT_BUTTON = ("Microsoft YaHei", 13)
FONT_SMALL = ("Microsoft YaHei", 11)
FONT_COUNTER = ("Microsoft YaHei", 12)

# ── 中文字符串 ──
STR_APP_TITLE = "番茄钟"
STR_PHASE_IDLE = "准备开始"
STR_PHASE_WORK = "专注工作"
STR_PHASE_SHORT_BREAK = "短休息"
STR_PHASE_LONG_BREAK = "长休息"
STR_PHASE_PAUSED = "已暂停"
STR_START = "开始"
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
