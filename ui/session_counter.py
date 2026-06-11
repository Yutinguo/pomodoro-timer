"""今日番茄计数显示"""

import customtkinter as ctk

import config as cfg
from state_manager import StateManager


class SessionCounter(ctk.CTkFrame):
    """显示今日完成的番茄数"""

    def __init__(self, parent, state_manager: StateManager):
        super().__init__(parent, fg_color="transparent")
        self._sm = state_manager

        # 番茄图标行
        self._icons_label = ctk.CTkLabel(
            self,
            text="",
            font=("", 18),
            text_color=cfg.COLOR_ACCENT_WORK,
        )
        self._icons_label.pack()

        # 计数文字
        self._label = ctk.CTkLabel(
            self,
            text="",
            font=cfg.FONT_COUNTER,
            text_color=cfg.COLOR_TEXT_SECONDARY,
        )
        self._label.pack(pady=(0, 0))

        self._sm.subscribe(self._on_state_changed)
        self._render(self._sm.state)

    def _on_state_changed(self, state):
        self._render(state)

    def _render(self, state):
        count = state.sessions_completed
        if count == 0:
            self._icons_label.configure(text="—", text_color=cfg.COLOR_TEXT_SECONDARY)
        else:
            tomatoes = "🍅 " * min(count, 12)  # 最多显示12个
            self._icons_label.configure(text=tomatoes.strip(), text_color=cfg.COLOR_ACCENT_WORK)

        self._label.configure(
            text=f"{cfg.STR_TODAY_COUNT}  {count}"
        )
