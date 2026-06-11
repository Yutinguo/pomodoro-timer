"""主窗口 — 组装所有 UI 组件，处理窗口事件"""

import customtkinter as ctk

import config as cfg
from state_manager import StateManager
from ui.progress_ring import ProgressRing
from ui.controls import ControlPanel
from ui.session_counter import SessionCounter
from ui.settings_panel import SettingsPanel


class MainWindow(ctk.CTk):
    """番茄钟主窗口"""

    def __init__(self, state_manager: StateManager):
        super().__init__()

        self._sm = state_manager

        # ── 窗口基本设置 ──
        self.title(cfg.STR_APP_TITLE)
        self.geometry(f"{cfg.WINDOW_WIDTH}x{cfg.WINDOW_HEIGHT}")
        self.minsize(cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT)
        self.resizable(False, False)

        # 窗口居中
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - cfg.WINDOW_WIDTH) // 2
        y = (screen_h - cfg.WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        # 关闭按钮行为：最小化到托盘（由 tray.py 绑定）
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── 顶部标题 ──
        self._title_label = ctk.CTkLabel(
            self,
            text="🍅 " + cfg.STR_APP_TITLE,
            font=("Microsoft YaHei", 20, "bold"),
            text_color=cfg.COLOR_ACCENT_WORK,
        )
        self._title_label.pack(pady=(20, 10))

        # ── 圆环进度条 ──
        self._progress_ring = ProgressRing(self, self._sm)
        self._progress_ring.pack(pady=(0, 10))

        # ── 今日番茄计数 ──
        self._session_counter = SessionCounter(self, self._sm)
        self._session_counter.pack(pady=(0, 15))

        # ── 控制按钮 ──
        self._controls = ControlPanel(self, self._sm)
        self._controls.pack(pady=(0, 15))

        # ── 设置面板 ──
        self._settings = SettingsPanel(self, self._sm)
        self._settings.pack(pady=(0, 20))

        # ── 状态变更时更新置顶 ──
        self._sm.subscribe(self._on_state_changed)

    def _on_state_changed(self, state):
        self.attributes("-topmost", state.always_on_top)

    def _on_close(self):
        """点击关闭按钮时最小化到托盘"""
        self.withdraw()  # 隐藏窗口而非退出
