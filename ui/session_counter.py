"""今日番茄计数显示"""

import customtkinter as ctk

import config as cfg
from state_manager import StateManager


class SessionCounter(ctk.CTkFrame):
    """显示今日完成的番茄数"""

    def __init__(self, parent, state_manager: StateManager):
        super().__init__(parent, fg_color="transparent")
        self._sm = state_manager

        self._label = ctk.CTkLabel(
            self,
            text="",
            font=cfg.FONT_COUNTER,
            text_color=cfg.COLOR_TEXT_SECONDARY,
        )
        self._label.pack()

        self._sm.subscribe(self._on_state_changed)
        self._render(self._sm.state)

    def _on_state_changed(self, state):
        self._render(state)

    def _render(self, state):
        tomatoes = "🍅" * state.sessions_completed
        if state.sessions_completed == 0:
            tomatoes = "—"
        self._label.configure(
            text=f"{cfg.STR_TODAY_COUNT}: {state.sessions_completed}  {tomatoes}"
        )
