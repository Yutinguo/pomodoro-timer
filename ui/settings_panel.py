"""设置面板 — 窗口置顶 / 声音开关"""

import customtkinter as ctk

import config as cfg
from state_manager import StateManager


class SettingsPanel(ctk.CTkFrame):
    """设置开关面板"""

    def __init__(self, parent, state_manager: StateManager):
        super().__init__(parent, fg_color="transparent")
        self._sm = state_manager

        # ── 窗口置顶开关 ──
        self._top_var = ctk.BooleanVar(value=False)
        self._top_switch = ctk.CTkSwitch(
            self,
            text=cfg.STR_ALWAYS_ON_TOP,
            variable=self._top_var,
            command=self._toggle_top,
            font=cfg.FONT_SMALL,
            text_color=cfg.COLOR_TEXT_SECONDARY,
            fg_color=cfg.COLOR_TOGGLE_OFF,
            progress_color=cfg.COLOR_TOGGLE_ON,
        )
        self._top_switch.pack(side="left", padx=12)

        # ── 声音开关 ──
        self._sound_var = ctk.BooleanVar(value=True)
        self._sound_switch = ctk.CTkSwitch(
            self,
            text=cfg.STR_SOUND,
            variable=self._sound_var,
            command=self._toggle_sound,
            font=cfg.FONT_SMALL,
            text_color=cfg.COLOR_TEXT_SECONDARY,
            fg_color=cfg.COLOR_TOGGLE_OFF,
            progress_color=cfg.COLOR_TOGGLE_ON,
        )
        self._sound_switch.pack(side="left", padx=12)

        self._sm.subscribe(self._on_state_changed)

    def _toggle_top(self):
        is_on = self._sm.toggle_always_on_top()
        # 实际的置顶操作由 main_window 处理

    def _toggle_sound(self):
        self._sm.toggle_sound()

    def _on_state_changed(self, state):
        if self._top_var.get() != state.always_on_top:
            self._top_var.set(state.always_on_top)
        if self._sound_var.get() != state.sound_enabled:
            self._sound_var.set(state.sound_enabled)
