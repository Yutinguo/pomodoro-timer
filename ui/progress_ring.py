"""圆环进度条 — Canvas 绘制环形倒计时"""

import tkinter as tk
from math import pi

import customtkinter as ctk

import config as cfg
from state_manager import StateManager


class ProgressRing(ctk.CTkFrame):
    """自定义圆环进度条组件"""

    def __init__(self, parent, state_manager: StateManager):
        super().__init__(parent, fg_color="transparent")
        self._sm = state_manager

        size = cfg.PROGRESS_RING_SIZE
        self._canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            bg=cfg.COLOR_BG,
            highlightthickness=0,
        )
        self._canvas.pack()

        # 注册状态变更
        self._sm.subscribe(self._on_state_changed)

        # 初始绘制
        self._render(self._sm.state)

    def _on_state_changed(self, state):
        self._render(state)

    def _get_phase_color(self, phase: str) -> str:
        if phase in ("work", "paused"):
            return cfg.COLOR_ACCENT_WORK
        elif phase == "short_break":
            return cfg.COLOR_ACCENT_SHORT_BREAK
        elif phase == "long_break":
            return cfg.COLOR_ACCENT_LONG_BREAK
        return cfg.COLOR_ACCENT_WORK  # idle

    def _get_phase_label(self, phase: str) -> str:
        return {
            "idle": cfg.STR_PHASE_IDLE,
            "work": cfg.STR_PHASE_WORK,
            "paused": cfg.STR_PHASE_PAUSED,
            "short_break": cfg.STR_PHASE_SHORT_BREAK,
            "long_break": cfg.STR_PHASE_LONG_BREAK,
        }.get(phase, "")

    def _render(self, state):
        canvas = self._canvas
        canvas.delete("all")

        size = cfg.PROGRESS_RING_SIZE
        width = cfg.PROGRESS_RING_WIDTH
        cx, cy = size // 2, size // 2
        r = (size // 2) - width - 4

        bbox = (cx - r, cy - r, cx + r, cy + r)
        bbox_outer = (cx - r - width // 2, cy - r - width // 2,
                      cx + r + width // 2, cy + r + width // 2)

        # ── 背景轨道 ──
        canvas.create_arc(
            bbox, start=270, extent=-359.9,
            style="arc", outline=cfg.COLOR_RING_TRACK,
            width=width,
        )

        # ── 进度弧 ──
        if state.total_seconds > 0:
            fraction = state.remaining_seconds / state.total_seconds
            # 从 12 点钟方向逆时针
            extent = -fraction * 359.9
        else:
            extent = 0

        color = self._get_phase_color(state.phase)
        if state.phase == "idle":
            extent = -359.9  # idle 时显示完整圆环

        canvas.create_arc(
            bbox, start=270, extent=extent,
            style="arc", outline=color,
            width=width,
        )
        # 在圆弧两端加小圆点，模拟圆角端点
        if extent != -359.9 and abs(extent) > 0:
            import math
            # 圆弧终点（12 点钟 = 270°，顺时针为正，extent 为负）
            end_angle = math.radians(270 + extent)
            ex = cx + r * math.cos(end_angle)
            ey = cy + r * math.sin(end_angle)
            dot_r = width // 2
            canvas.create_oval(
                ex - dot_r, ey - dot_r,
                ex + dot_r, ey + dot_r,
                fill=color, outline="",
            )

        # ── 中心时间文字 ──
        minutes = state.remaining_seconds // 60
        seconds = state.remaining_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        canvas.create_text(
            cx, cy - 12,
            text=time_str,
            font=cfg.FONT_TIMER,
            fill=cfg.COLOR_TEXT,
        )

        # ── 阶段标签 ──
        label = self._get_phase_label(state.phase)
        canvas.create_text(
            cx, cy + 36,
            text=label,
            font=cfg.FONT_LABEL,
            fill=self._get_phase_color(state.phase),
        )
