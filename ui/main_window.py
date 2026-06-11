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
        self.configure(fg_color=cfg.COLOR_BG)

        # 窗口居中
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - cfg.WINDOW_WIDTH) // 2
        y = (screen_h - cfg.WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        # 关闭按钮行为：最小化到托盘
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── 顶部番茄图标 ──
        self._icon_label = ctk.CTkLabel(
            self,
            text="🍅",
            font=("", 28),
        )
        self._icon_label.pack(pady=(24, 0))

        # ── 圆环进度条 ──
        self._progress_ring = ProgressRing(self, self._sm)
        self._progress_ring.pack(pady=(6, 14))

        # ── 今日番茄计数 ──
        self._session_counter = SessionCounter(self, self._sm)
        self._session_counter.pack(pady=(0, 18))

        # ── 控制按钮 ──
        self._controls = ControlPanel(self, self._sm)
        self._controls.pack(pady=(0, 20))

        # ── 设置面板 ──
        self._settings = SettingsPanel(self, self._sm)
        self._settings.pack(pady=(0, 20))

        # ── 状态变更时更新置顶 ──
        self._sm.subscribe(self._on_state_changed)

    def _on_state_changed(self, state):
        self.attributes("-topmost", state.always_on_top)

    def _on_close(self):
        """点击关闭按钮时最小化到托盘"""
        self.withdraw()
