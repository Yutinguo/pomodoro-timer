"""圆环进度条 — Canvas 绘制环形倒计时，含光晕、纹理、动画"""

import math
import tkinter as tk

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

        # 动画状态
        self._anim_extent = 0       # 当前动画中的弧度（可能不等同 state）
        self._anim_target = 0       # 目标弧度
        self._anim_after_id = None  # 动画 after ID
        self._breath_after_id = None  # 呼吸动画 ID
        self._breath_phase = 0.0    # 呼吸透明度相位
        self._breath_dir = 1        # 呼吸方向

        # 注册状态变更
        self._sm.subscribe(self._on_state_changed)

        # 绘制背景纹理（只画一次）
        self._draw_texture()

        # 初始渲染
        state = self._sm.state
        self._anim_extent = self._extent_from_state(state)
        self._anim_target = self._anim_extent
        self._render(state)

        # idle 时启动呼吸动画
        if state.phase == "idle":
            self._start_breathing()

    # ── 背景纹理 ──

    def _draw_texture(self):
        """绘制微妙的网点纹理背景"""
        size = cfg.PROGRESS_RING_SIZE
        spacing = 16
        dot_r = 0.8
        for x in range(spacing, size, spacing):
            for y in range(spacing, size, spacing):
                self._canvas.create_oval(
                    x - dot_r, y - dot_r,
                    x + dot_r, y + dot_r,
                    fill=cfg.COLOR_DOT_PATTERN, outline="",
                    tags="texture",
                )

    # ── 弧度计算 ──

    def _extent_from_state(self, state) -> float:
        if state.phase == "idle":
            return -359.9
        if state.total_seconds > 0:
            fraction = state.remaining_seconds / state.total_seconds
            return -fraction * 359.9
        return 0

    # ── 状态变更 ──

    def _on_state_changed(self, state):
        # 停止呼吸
        self._stop_breathing()

        target = self._extent_from_state(state)

        if state.phase == "idle":
            # 回到 idle：动画过渡到完整圆环然后开始呼吸
            self._animate_to(target, done_callback=self._start_breathing)
        elif state.phase == "paused":
            # 暂停：直接设置
            self._cancel_animation()
            self._anim_extent = target
            self._anim_target = target
            self._render(state)
        else:
            # 其他状态：动画过渡
            self._animate_to(target)

        self._render(state)

    # ── 动画 ──

    def _animate_to(self, target: float, done_callback=None):
        """平滑过渡到目标弧度"""
        self._cancel_animation()
        self._anim_target = target

        # 如果差异很小，直接到位
        if abs(self._anim_extent - target) < 1:
            self._anim_extent = target
            self._render(self._sm.state)
            if done_callback:
                done_callback()
            return

        self._anim_step(target, done_callback)

    def _anim_step(self, target: float, done_callback=None):
        """单步动画（线性插值，~20fps）"""
        diff = target - self._anim_extent
        step = diff * 0.3  # easing: 每帧移 30% 剩余距离

        if abs(diff) < 0.5:
            self._anim_extent = target
            self._render(self._sm.state)
            if done_callback:
                done_callback()
            return

        self._anim_extent += step
        self._render(self._sm.state)
        self._anim_after_id = self._canvas.after(
            16, lambda: self._anim_step(target, done_callback)
        )

    def _cancel_animation(self):
        if self._anim_after_id is not None:
            self._canvas.after_cancel(self._anim_after_id)
            self._anim_after_id = None

    # ── 呼吸动画 ──

    def _start_breathing(self):
        """idle 状态下的呼吸脉冲"""
        if self._sm.state.phase != "idle":
            return
        self._breath_phase = 0.0
        self._breath_dir = 1
        self._breath_step()

    def _breath_step(self):
        if self._sm.state.phase != "idle":
            self._stop_breathing()
            return

        self._breath_phase += 0.04 * self._breath_dir
        if self._breath_phase >= 1.0:
            self._breath_phase = 1.0
            self._breath_dir = -1
        elif self._breath_phase <= 0.0:
            self._breath_phase = 0.0
            self._breath_dir = 1

        self._render(self._sm.state)
        self._breath_after_id = self._canvas.after(50, self._breath_step)

    def _stop_breathing(self):
        if self._breath_after_id is not None:
            self._canvas.after_cancel(self._breath_after_id)
            self._breath_after_id = None

    # ── 颜色映射 ──

    def _get_phase_color(self, phase: str) -> str:
        if phase == "work":
            return cfg.COLOR_ACCENT_WORK
        elif phase == "paused":
            return cfg.COLOR_PAUSE
        elif phase == "short_break":
            return cfg.COLOR_ACCENT_SHORT_BREAK
        elif phase == "long_break":
            return cfg.COLOR_ACCENT_LONG_BREAK
        return cfg.COLOR_IDLE_RING  # idle

    def _get_phase_label(self, phase: str) -> str:
        return {
            "idle": cfg.STR_PHASE_IDLE,
            "work": cfg.STR_PHASE_WORK,
            "paused": cfg.STR_PHASE_PAUSED,
            "short_break": cfg.STR_PHASE_SHORT_BREAK,
            "long_break": cfg.STR_PHASE_LONG_BREAK,
        }.get(phase, "")

    # ── 渲染 ──

    def _render(self, state):
        canvas = self._canvas
        # 保留 texture 元素，只删除动态元素
        canvas.delete("dynamic")

        size = cfg.PROGRESS_RING_SIZE
        width = cfg.PROGRESS_RING_WIDTH
        cx, cy = size // 2, size // 2
        r = (size // 2) - width - 8

        bbox = (cx - r, cy - r, cx + r, cy + r)

        color = self._get_phase_color(state.phase)
        phase_label = self._get_phase_label(state.phase)

        # ── 外光晕（仅在运行时显示） ──
        if state.phase != "idle" and state.phase != "paused":
            glow_width = width + 10
            glow_bbox = (
                cx - r - 5, cy - r - 5,
                cx + r + 5, cy + r + 5,
            )
            # 三层光晕，从宽到窄
            for i, (gw, galpha_color) in enumerate([
                (glow_width, "#3a1f18"),
                (glow_width + 4, "#2d1813"),
                (glow_width + 8, "#201310"),
            ]):
                canvas.create_arc(
                    glow_bbox,
                    start=270,
                    extent=self._anim_extent if self._anim_extent != -359.9 else -359.9,
                    style="arc",
                    outline=galpha_color,
                    width=gw - i * 3,
                    tags="dynamic",
                )

        # ── 背景轨道（带内阴影） ──
        # 外层轨道 — 稍亮
        canvas.create_arc(
            (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2),
            start=270, extent=-359.9,
            style="arc", outline="#221815",
            width=width + 4,
            tags="dynamic",
        )
        # 主轨道
        canvas.create_arc(
            bbox, start=270, extent=-359.9,
            style="arc", outline=cfg.COLOR_RING_TRACK,
            width=width,
            tags="dynamic",
        )

        # ── idle 呼吸效果 ──
        if state.phase == "idle":
            breath_intensity = 0.15 + 0.25 * self._breath_phase
            # 额外的呼吸圆环
            breath_r = r - width // 2 - 1
            breath_bbox = (cx - breath_r, cy - breath_r, cx + breath_r, cy + breath_r)
            # 通过改变颜色亮度模拟呼吸
            r_val = int(0x3d + (0x55 - 0x3d) * breath_intensity)
            g_val = int(0x30 + (0x40 - 0x30) * breath_intensity)
            b_val = int(0x2b + (0x38 - 0x2b) * breath_intensity)
            breath_color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"

            canvas.create_arc(
                bbox, start=270, extent=-359.9,
                style="arc", outline=breath_color,
                width=width + 1,
                tags="dynamic",
            )

        # ── 进度弧 — 用动画中的弧度 ──
        extent = self._anim_extent

        # 进度弧阴影
        canvas.create_arc(
            (cx - r + 1, cy - r + 1, cx + r + 1, cy + r + 1),
            start=270, extent=extent,
            style="arc", outline="#000000",
            width=width,
            tags="dynamic",
        )

        # 进度弧主体
        canvas.create_arc(
            bbox, start=270, extent=extent,
            style="arc", outline=color,
            width=width,
            tags="dynamic",
        )

        # ── 弧端点高亮圆点 ──
        if extent != -359.9 and abs(extent) > 0:
            end_angle = math.radians(270 + extent)
            ex = cx + r * math.cos(end_angle)
            ey = cy + r * math.sin(end_angle)
            dot_r = width // 2 + 1

            # 辉光
            canvas.create_oval(
                ex - dot_r - 3, ey - dot_r - 3,
                ex + dot_r + 3, ey + dot_r + 3,
                fill="", outline=color, width=1,
                tags="dynamic",
            )
            # 主体
            canvas.create_oval(
                ex - dot_r, ey - dot_r,
                ex + dot_r, ey + dot_r,
                fill=color, outline="",
                tags="dynamic",
            )

        # ── 中心时间文字（带微阴影） ──
        minutes = state.remaining_seconds // 60
        seconds = state.remaining_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        # 阴影
        canvas.create_text(
            cx + 1, cy - 10 + 1,
            text=time_str,
            font=cfg.FONT_TIMER,
            fill="#0d0a09",
            tags="dynamic",
        )
        # 主体
        canvas.create_text(
            cx, cy - 10,
            text=time_str,
            font=cfg.FONT_TIMER,
            fill=cfg.COLOR_TEXT,
            tags="dynamic",
        )

        # ── 阶段标签 ──
        canvas.create_text(
            cx, cy + 38,
            text=phase_label,
            font=cfg.FONT_LABEL,
            fill=self._get_phase_color(state.phase),
            tags="dynamic",
        )

    def destroy(self):
        self._cancel_animation()
        self._stop_breathing()
        super().destroy()
