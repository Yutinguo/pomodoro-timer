"""状态管理器 — 观察者模式，管理番茄钟所有状态"""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Callable

import config as cfg


@dataclass
class TimerState:
    """不可变状态对象"""
    phase: str = "idle"          # idle | work | short_break | long_break | paused
    remaining_seconds: int = cfg.WORK_DURATION
    total_seconds: int = cfg.WORK_DURATION
    sessions_completed: int = 0  # 今日完成番茄数
    is_running: bool = False
    always_on_top: bool = False
    sound_enabled: bool = True
    # 用于暂停恢复：暂停前处于什么阶段
    _phase_before_pause: str = "work"


class StateManager:
    """单例状态管理器，负责状态变更和通知订阅者"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._state = TimerState()
        self._subscribers: list[Callable[[TimerState], None]] = []
        self._on_phase_done: Callable[[], None] | None = None  # 阶段结束回调

        # 加载今日番茄数
        self._state = TimerState(
            sessions_completed=self._load_today_count()
        )

    # ── 属性访问 ──

    @property
    def state(self) -> TimerState:
        return self._state

    # ── 订阅 ──

    def subscribe(self, callback: Callable[[TimerState], None]):
        """订阅状态变更，回调接收最新的 TimerState"""
        self._subscribers.append(callback)

    def set_phase_done_callback(self, callback: Callable[[], None]):
        """设置阶段结束回调（由 TimerEngine 使用）"""
        self._on_phase_done = callback

    def _notify(self):
        for cb in self._subscribers:
            try:
                cb(self._state)
            except Exception:
                pass

    # ── 操作 ──

    def start(self):
        """开始计时"""
        s = self._state
        if s.is_running:
            return

        if s.phase == "paused":
            # 从暂停恢复
            self._state = TimerState(
                phase=s._phase_before_pause,
                remaining_seconds=s.remaining_seconds,
                total_seconds=s.total_seconds,
                sessions_completed=s.sessions_completed,
                is_running=True,
                always_on_top=s.always_on_top,
                sound_enabled=s.sound_enabled,
                _phase_before_pause=s._phase_before_pause,
            )
        else:
            # 全新开始
            self._state = TimerState(
                phase="work",
                remaining_seconds=cfg.WORK_DURATION,
                total_seconds=cfg.WORK_DURATION,
                sessions_completed=s.sessions_completed,
                is_running=True,
                always_on_top=s.always_on_top,
                sound_enabled=s.sound_enabled,
                _phase_before_pause="work",
            )
        self._notify()

    def pause(self):
        """暂停计时"""
        s = self._state
        if not s.is_running or s.phase == "idle":
            return

        self._state = TimerState(
            phase="paused",
            remaining_seconds=s.remaining_seconds,
            total_seconds=s.total_seconds,
            sessions_completed=s.sessions_completed,
            is_running=False,
            always_on_top=s.always_on_top,
            sound_enabled=s.sound_enabled,
            _phase_before_pause=s.phase,
        )
        self._notify()

    def reset(self):
        """重置回 idle 状态"""
        s = self._state
        self._state = TimerState(
            phase="idle",
            remaining_seconds=cfg.WORK_DURATION,
            total_seconds=cfg.WORK_DURATION,
            sessions_completed=s.sessions_completed,
            is_running=False,
            always_on_top=s.always_on_top,
            sound_enabled=s.sound_enabled,
            _phase_before_pause="work",
        )
        self._notify()

    def skip(self):
        """跳过当前阶段，直接触发阶段结束"""
        s = self._state
        if s.phase == "idle":
            return
        self._state = TimerState(
            phase=s.phase,
            remaining_seconds=0,
            total_seconds=s.total_seconds,
            sessions_completed=s.sessions_completed,
            is_running=s.is_running,
            always_on_top=s.always_on_top,
            sound_enabled=s.sound_enabled,
            _phase_before_pause=s._phase_before_pause,
        )
        self._notify()
        # 立即触发阶段结束
        if self._on_phase_done:
            self._on_phase_done()

    def tick(self, remaining_seconds: int):
        """每秒更新剩余时间（由 TimerEngine 调用）"""
        s = self._state
        self._state = TimerState(
            phase=s.phase,
            remaining_seconds=max(0, remaining_seconds),
            total_seconds=s.total_seconds,
            sessions_completed=s.sessions_completed,
            is_running=s.is_running,
            always_on_top=s.always_on_top,
            sound_enabled=s.sound_enabled,
            _phase_before_pause=s._phase_before_pause,
        )
        self._notify()

    def transition_phase(self):
        """阶段结束，自动切换到下一阶段"""
        s = self._state
        now = time.time()

        if s.phase == "work":
            # 完成一个番茄
            new_count = s.sessions_completed + 1
            self._save_today_count(new_count)

            if new_count % cfg.POMODOROS_PER_CYCLE == 0:
                next_phase = "long_break"
                next_total = cfg.LONG_BREAK_DURATION
            else:
                next_phase = "short_break"
                next_total = cfg.SHORT_BREAK_DURATION

            self._state = TimerState(
                phase=next_phase,
                remaining_seconds=next_total,
                total_seconds=next_total,
                sessions_completed=new_count,
                is_running=True,
                always_on_top=s.always_on_top,
                sound_enabled=s.sound_enabled,
                _phase_before_pause=next_phase,
            )

        elif s.phase in ("short_break", "long_break"):
            # 休息结束，开始新工作阶段
            self._state = TimerState(
                phase="work",
                remaining_seconds=cfg.WORK_DURATION,
                total_seconds=cfg.WORK_DURATION,
                sessions_completed=s.sessions_completed,
                is_running=True,
                always_on_top=s.always_on_top,
                sound_enabled=s.sound_enabled,
                _phase_before_pause="work",
            )

        self._notify()

    # ── 设置项 ──

    def toggle_always_on_top(self):
        s = self._state
        self._state = TimerState(
            phase=s.phase,
            remaining_seconds=s.remaining_seconds,
            total_seconds=s.total_seconds,
            sessions_completed=s.sessions_completed,
            is_running=s.is_running,
            always_on_top=not s.always_on_top,
            sound_enabled=s.sound_enabled,
            _phase_before_pause=s._phase_before_pause,
        )
        self._notify()
        return self._state.always_on_top

    def toggle_sound(self):
        s = self._state
        self._state = TimerState(
            phase=s.phase,
            remaining_seconds=s.remaining_seconds,
            total_seconds=s.total_seconds,
            sessions_completed=s.sessions_completed,
            is_running=s.is_running,
            always_on_top=s.always_on_top,
            sound_enabled=not s.sound_enabled,
            _phase_before_pause=s._phase_before_pause,
        )
        self._notify()
        return self._state.sound_enabled

    # ── 持久化 ──

    def _data_dir(self) -> str:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        path = os.path.join(appdata, cfg.APP_DATA_DIR_NAME)
        os.makedirs(path, exist_ok=True)
        return path

    def _session_file(self) -> str:
        return os.path.join(self._data_dir(), cfg.SESSION_FILE_NAME)

    def _load_today_count(self) -> int:
        today = time.strftime("%Y-%m-%d")
        try:
            with open(self._session_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("date") == today:
                return data.get("count", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return 0

    def _save_today_count(self, count: int):
        today = time.strftime("%Y-%m-%d")
        try:
            with open(self._session_file(), "w", encoding="utf-8") as f:
                json.dump({"date": today, "count": count}, f)
        except OSError:
            pass
