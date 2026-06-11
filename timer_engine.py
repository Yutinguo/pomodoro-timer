"""倒计时引擎 — 基于时间戳的高精度计时，避免 tk.after() 漂移"""

import time


class TimerEngine:
    """管理倒计时循环，基于 wall clock 计算剩余时间"""

    def __init__(self, state_manager, root):
        self._sm = state_manager
        self._root = root
        self._start_time: float = 0.0   # 当前阶段开始的时间戳
        self._total_seconds: int = 0     # 当前阶段总秒数
        self._after_id: str | None = None  # tk.after 的 ID

        # 注册阶段结束回调
        self._sm.set_phase_done_callback(self._on_phase_done)

        # 订阅状态变更，以在 pause/resume/reset 时同步
        self._sm.subscribe(self._on_state_changed)
        self._last_phase = self._sm.state.phase
        self._was_running = self._sm.state.is_running

    def _on_state_changed(self, state):
        """响应状态变更，管理计时循环的启停"""
        prev_phase = self._last_phase
        prev_running = self._was_running
        self._last_phase = state.phase
        self._was_running = state.is_running

        # 从非运行 → 运行：启动计时
        if state.is_running and not prev_running:
            self._start_time = time.time()
            self._total_seconds = state.total_seconds
            self._schedule_tick()

        # 从运行 → 非运行（暂停/重置）：停止计时
        elif not state.is_running and prev_running:
            self._cancel_tick()

        # 阶段切换（transition_phase 触发）
        if state.is_running and state.phase != prev_phase and prev_phase not in ("idle", "paused"):
            self._start_time = time.time()
            self._total_seconds = state.total_seconds

    def _schedule_tick(self):
        """安排下一次 tick（约 200ms 后，比每秒更频繁以保证 UI 流畅）"""
        self._cancel_tick()
        self._after_id = self._root.after(200, self._tick)

    def _cancel_tick(self):
        if self._after_id is not None:
            self._root.after_cancel(self._after_id)
            self._after_id = None

    def _tick(self):
        """每次 tick：根据墙钟计算剩余时间并更新状态"""
        state = self._sm.state
        if not state.is_running:
            return

        elapsed = time.time() - self._start_time
        remaining = int(self._total_seconds - elapsed)

        if remaining <= 0:
            # 时间到
            self._sm.tick(0)
            self._on_phase_done()
        else:
            self._sm.tick(remaining)
            self._schedule_tick()

    def _on_phase_done(self):
        """当前阶段结束，触发过渡"""
        self._cancel_tick()
        self._sm.transition_phase()
        # transition_phase 会设置新阶段的 is_running=True，
        # _on_state_changed 会自动启动新的计时循环
