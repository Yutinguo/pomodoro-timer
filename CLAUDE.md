# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

番茄钟（Pomodoro Timer）桌面应用 — Python 3.13 + CustomTkinter 构建的 Windows 桌面计时器。

## 环境与仓库

- **Python**: 3.13.11（Miniconda）
- **Shell**: Bash（Git Bash），使用 Unix 风格路径（`/`）
- **平台**: Windows 11
- **Git**: `git@github.com:Yutinguo/pomodoro-timer.git`，分支 `main`

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py

# 测试导入和状态逻辑（无需 GUI）
python -c "from state_manager import StateManager; sm = StateManager(); sm.start(); print(sm.state)"
```

## 架构

### 数据流（单向）

```
用户操作 → ControlPanel._on_main_click()
         → StateManager.start() / pause() / reset() / skip()
         → 创建新 TimerState → _notify() 所有订阅者
         → UI 组件根据新状态渲染 (ProgressRing, ControlPanel, SessionCounter, SettingsPanel)
         → MainWindow 更新置顶属性

TimerEngine._tick()（200ms 循环）
         → StateManager.tick(remaining) → _notify()
         → 若 remaining ≤ 0 → StateManager.transition_phase()

main.py 中 _setup_phase_notifications()（额外订阅者）
         → 检测 phase 变更 → 发通知 + 播放声音
```

### 核心模块

| 文件 | 职责 |
|------|------|
| `main.py` | 入口：设置 CTk 主题 → 创建 StateManager → 创建 MainWindow → 启动 TimerEngine → 注册通知/声音订阅者 → 启动 TrayManager → `mainloop()`。首次运行自动生成 `assets/tomato.ico` 和 `assets/alert.wav` |
| `config.py` | 所有常量：6 种时长、14 种颜色、5 种字体大小、18 个中文字符串 |
| `state_manager.py` | **核心**：`TimerState` 不可变 dataclass + `StateManager` 单例（观察者模式）。所有状态变更通过创建新 TimerState 实例实现 |
| `timer_engine.py` | 倒计时引擎：200ms tick 循环，基于 `time.time()` 墙上时钟计算剩余秒数 |

#### `StateManager` 关键操作

| 方法 | 触发时机 | 效果 |
|------|----------|------|
| `start()` | 点击"开始" | idle→work（新开始）或 paused→原阶段（恢复） |
| `pause()` | 点击"暂停" | 保存当前 phase 到 `_phase_before_pause`，phase→paused |
| `reset()` | 点击"重置" | phase→idle，剩余时间重置，保留今日番茄数 |
| `skip()` | 点击"跳过" | remaining→0 然后立即调用 `_on_phase_done` 触发阶段切换 |
| `tick(n)` | TimerEngine 每 200ms 调用 | 仅更新 remaining_seconds |
| `transition_phase()` | 阶段计时结束 | work→break（番茄+1 并持久化）或 break→work |

#### `TimerEngine` 设计要点

- **200ms tick** 而非 1000ms，确保 UI 圆环进度条每 200ms 更新一次，视觉更流畅
- **时间戳防漂移**：存 `start_time`，每次 tick 计算 `total - (now - start_time)`，不依赖 `after()` 累积
- **暂停恢复**：`_on_state_changed` 检测 `is_running` 变化，自动启停 tick 循环
- **阶段切换**：`transition_phase` 设置新阶段的 `is_running=True`，`_on_state_changed` 自动重启循环

### UI 组件（`ui/`）

| 文件 | 组件 | 订阅后更新的内容 |
|------|------|-----------------|
| `main_window.py` | `MainWindow(CTk)` | `-topmost` 属性；关闭→`withdraw()` 最小化到托盘 |
| `progress_ring.py` | `ProgressRing(CTkFrame)` | Canvas 圆弧弧度 + 中心时间文字 + 阶段标签 |
| `controls.py` | `ControlPanel(CTkFrame)` | 主按钮文字/颜色、跳过/重置按钮的启用状态 |
| `session_counter.py` | `SessionCounter(CTkFrame)` | 数字 + 🍅 emoji 串 |
| `settings_panel.py` | `SettingsPanel(CTkFrame)` | 两个 switch 的位置同步 |

### 服务层（`services/`）

| 文件 | 职责 | 依赖 |
|------|------|------|
| `notification.py` | 桌面通知 | `plyer` |
| `sound.py` | 播放 WAV 提示音 | `winsound`（Windows 标准库），`SND_ASYNC` 非阻塞 |
| `tray.py` | 系统托盘图标 + 右键菜单（显示/置顶/退出） | `pystray`（守护线程），通过 `window.after()` 回主线程 |

### 状态机

```
IDLE ──[start]──> WORK ──[timeout, count%4<4]──> SHORT_BREAK ──[timeout]──> WORK
                     │                                              │
                     └──[timeout, count%4=0]──> LONG_BREAK ──[timeout]──> WORK
                     │
                     ├──[pause]──> PAUSED ──[start]──> 恢复原阶段
                     │
                     └──[skip]──> 等价于 timeout（立即阶段切换）

任意阶段 ──[reset]──> IDLE
```

### 状态对象（`TimerState`）

不可变 frozen dataclass，字段：
`phase`, `remaining_seconds`, `total_seconds`, `sessions_completed`, `is_running`, `always_on_top`, `sound_enabled`, `_phase_before_pause`

`_phase_before_pause` 记录暂停前处于哪个阶段，用于 resume 时恢复正确的阶段和颜色。

### 持久化

每日番茄完成数存 JSON 到 `%APPDATA%/pomodoro_timer/sessions.json`，格式 `{"date": "2026-06-11", "count": 3}`。`_load_today_count()` 在启动时检查日期，若非今日则重置为 0。

## 关键设计决策

- **tkinter Canvas 自绘圆环**而非图片资源，颜色可随阶段动态切换。用 `create_oval` 在圆弧端点加小圆帽模拟圆角（tkinter 不支持 `capstyle`）
- **pystray 在守护线程运行**，tkinter 在主线程，跨线程通信必须通过 `window.after(0, callback)`
- **关闭窗口 = `withdraw()` 最小化到托盘**，真正退出需通过托盘右键"退出"
- **首次运行自动生成** 图标（ICO）和提示音（WAV），无需手动准备资源
- **所有状态变更创建新 TimerState**（不可变），确保订阅者拿到的是可比较的快照

## 行为准则

以下四条改编自 [Karpathy 对 LLM 编码的观察](https://github.com/forrestchang/andrej-karpathy-skills)，
约束本项目中 Claude Code 的行为方式。

### 1. 先想再写

不要假设，不要隐藏困惑，把取舍摆出来。

- 动手前先陈述你的假设。不确定就问。
- 如果存在多种解读，全列出来 — 不要默默选一个。
- 如果有更简单的做法，说出来。必要时 push back。
- 什么地方不清楚就停住，指明哪里困惑，请求确认。

> 本项目常见陷阱：tkinter 不是线程安全的，别从 pystray 线程直接操作 widget；
> CustomTkinter 用 `set_appearance_mode("dark")` 已全局设定，不要用原生 tk 覆盖主题色。

### 2. 简单优先

用最少代码解决问题。

- 不添加未要求的功能、不引入未使用的抽象、不做"以后可能用到"的扩展。
- 番茄钟是单用途桌面应用 — 不要引入数据库、ORM、插件系统、配置文件格式。
- 一个 `config.py` 管全部常量，比 JSON/YAML 配置简单直接，保持这个风格。
- 如果一段代码完成不了两个以上的任务，不要把它抽成单独的函数或类。

### 3. 精准修改

只动必要的代码。

- 不要"顺路清理"相邻文件。给 TimerState 加字段？只改 `state_manager.py`，别动 `timer_engine.py`。
- 保持现有代码风格一致 — 用 `# ── 注释分隔符 ──`，用 `cfg.` 前缀访问常量。
- 发现无关的 dead code 或问题，只提出来，不要顺手删掉。

### 4. 结果验证

把"帮我加个功能"变成可验证的目标。

- 修改完成后，运行以下验证之一：
  - 逻辑变更：`python -c "from state_manager import StateManager; ..."`
  - UI 变更：`python main.py`（窗口弹出后关闭即可）
  - 导入检查：确保所有模块仍可正常 import
- 如果某个变更无法用以上方式验证，在回复末尾说明验证方案。
- 改完 TimerState 要确认：subscribe 的组件数量没少、notify 没断链。

## additional instructions
- 当你需要对前端视觉进行修改的时候，去参考[text](品牌视觉规范)这个文件里的内容
- 当你要写产品文字的时候，参考[text](语言规范)这个文件里的内容