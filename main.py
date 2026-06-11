"""番茄钟 — 桌面版 Pomodoro Timer 入口"""

import os
import struct
import wave
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw

from config import (
    STR_APP_TITLE, STR_NOTIFICATION_WORK_DONE, STR_NOTIFICATION_BREAK_DONE,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)
from state_manager import StateManager
from timer_engine import TimerEngine
from ui.main_window import MainWindow
from services.notification import send_notification
from services.sound import play_alert
from services.tray import TrayManager


# ── 资源生成（首次运行时自动生成） ──

ASSETS_DIR = Path(__file__).parent / "assets"


def _generate_assets():
    """生成应用图标和提示音文件"""
    ASSETS_DIR.mkdir(exist_ok=True)

    # ── 生成 ICO 图标 ──
    ico_path = ASSETS_DIR / "tomato.ico"
    if not ico_path.exists():
        _create_tomato_icon(ico_path)

    # ── 生成 WAV 提示音 ──
    wav_path = ASSETS_DIR / "alert.wav"
    if not wav_path.exists():
        _create_alert_wav(wav_path)


def _create_tomato_icon(path):
    """用 Pillow 生成番茄图标"""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 3
    # 番茄主体
    draw.ellipse(
        [margin, margin + 10, size - margin, size - margin],
        fill="#e0554a",
    )
    # 绿叶
    leaf_top = (size // 2, margin)
    leaf_left = (size // 3, margin + 12)
    leaf_right = (size * 2 // 3, margin + 12)
    draw.polygon([leaf_top, leaf_left, leaf_right], fill="#7d9b76")

    img.save(path, format="ICO", sizes=[(64, 64)])


def _create_alert_wav(path):
    """生成一个简单的提示音 WAV 文件（双音调叮咚声）"""
    sample_rate = 44100
    duration = 0.4  # 秒
    freq1, freq2 = 880, 1100  # A5 和 C#6

    num_samples = int(sample_rate * duration)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # 前半段高频，后半段低频，快速衰减
        if t < duration * 0.5:
            val = int(16000 * (1 - t / duration) * _sine_wave(t, freq1))
        else:
            val = int(16000 * (1 - t / duration) * _sine_wave(t, freq2))
        samples.append(val)

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def _sine_wave(t, freq):
    import math
    return math.sin(2 * math.pi * freq * t)


# ── 阶段切换通知 ──

def _setup_phase_notifications(sm: StateManager):
    """监听阶段切换，发送通知和播放声音"""
    prev_phase = {"value": sm.state.phase}

    def on_state_changed(state):
        new_phase = state.phase
        old_phase = prev_phase["value"]
        prev_phase["value"] = new_phase

        # 只在阶段真正切换时触发（排除 idle 和 paused）
        if new_phase == old_phase:
            return
        if old_phase == "idle" or new_phase == "paused":
            return

        # 工作 → 休息
        if old_phase == "work" and new_phase in ("short_break", "long_break"):
            if state.sound_enabled:
                play_alert()
            send_notification(STR_APP_TITLE, STR_NOTIFICATION_WORK_DONE)

        # 休息 → 工作
        elif old_phase in ("short_break", "long_break") and new_phase == "work":
            if state.sound_enabled:
                play_alert()
            send_notification(STR_APP_TITLE, STR_NOTIFICATION_BREAK_DONE)

    sm.subscribe(on_state_changed)


# ── 入口 ──

def main():
    # 生成资源
    _generate_assets()

    # 设置外观
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # 创建核心模块
    sm = StateManager()
    window = MainWindow(sm)

    # 设置窗口图标
    ico_path = ASSETS_DIR / "tomato.ico"
    if ico_path.exists():
        window.iconbitmap(str(ico_path))

    # 计时引擎
    TimerEngine(sm, window)

    # 阶段切换通知
    _setup_phase_notifications(sm)

    # 系统托盘
    tray = TrayManager(window, sm)
    tray.setup()

    # 启动
    window.mainloop()


if __name__ == "__main__":
    main()
