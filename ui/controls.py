"""控制按钮面板 — 开始/暂停/继续/重置/跳过"""

import customtkinter as ctk

import config as cfg
from state_manager import StateManager


class ControlPanel(ctk.CTkFrame):
    """底部控制按钮"""

    def __init__(self, parent, state_manager: StateManager):
        super().__init__(parent, fg_color="transparent")
        self._sm = state_manager

        # ── 主按钮（开始/暂停/继续） ──
        self._main_btn = ctk.CTkButton(
            self,
            text=cfg.STR_START,
            font=cfg.FONT_BUTTON,
            width=120,
            height=40,
            corner_radius=20,
            fg_color=cfg.COLOR_ACCENT_WORK,
            hover_color=cfg.COLOR_BUTTON_HOVER,
            text_color=cfg.COLOR_BUTTON_TEXT,
            command=self._on_main_click,
        )
        self._main_btn.pack(side="left", padx=6)

        # ── 重置按钮 ──
        self._reset_btn = ctk.CTkButton(
            self,
            text=cfg.STR_RESET,
            font=cfg.FONT_SMALL,
            width=70,
            height=40,
            corner_radius=20,
            fg_color=cfg.COLOR_BUTTON,
            hover_color=cfg.COLOR_BUTTON_HOVER,
            text_color=cfg.COLOR_BUTTON_TEXT,
            command=self._sm.reset,
        )
        self._reset_btn.pack(side="left", padx=6)

        # ── 跳过按钮 ──
        self._skip_btn = ctk.CTkButton(
            self,
            text=cfg.STR_SKIP,
            font=cfg.FONT_SMALL,
            width=70,
            height=40,
            corner_radius=20,
            fg_color=cfg.COLOR_BUTTON,
            hover_color=cfg.COLOR_BUTTON_HOVER,
            text_color=cfg.COLOR_BUTTON_TEXT,
            command=self._sm.skip,
        )
        self._skip_btn.pack(side="left", padx=6)

        # 订阅状态
        self._sm.subscribe(self._on_state_changed)
        self._update_buttons(self._sm.state)

    def _on_state_changed(self, state):
        self._update_buttons(state)

    def _on_main_click(self):
        s = self._sm.state
        if s.phase == "paused":
            self._sm.start()  # resume
        elif s.is_running:
            self._sm.pause()
        else:
            self._sm.start()

    def _update_buttons(self, state):
        # 主按钮
        if state.is_running:
            self._main_btn.configure(text=cfg.STR_PAUSE, fg_color="#e67e22")
        elif state.phase == "paused":
            self._main_btn.configure(text=cfg.STR_RESUME, fg_color=cfg.COLOR_ACCENT_WORK)
        else:
            self._main_btn.configure(text=cfg.STR_START, fg_color=cfg.COLOR_ACCENT_WORK)

        # 跳过按钮：idle 时禁用
        if state.phase == "idle":
            self._skip_btn.configure(state="disabled")
        else:
            self._skip_btn.configure(state="normal")

        # 重置按钮：idle 时禁用
        if state.phase == "idle":
            self._reset_btn.configure(state="disabled")
        else:
            self._reset_btn.configure(state="normal")
