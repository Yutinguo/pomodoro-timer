# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

番茄钟（Pomodoro Timer）桌面应用 — Python 3.13 + CustomTkinter 构建的 Windows 桌面计时器。

## 环境

- **Python**: 3.13.11（Miniconda）
- **Shell**: Bash（Git Bash），使用 Unix 风格路径（`/`）
- **平台**: Windows 11
- **无 git 仓库**（尚未初始化）

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py

# 检查 Python 环境
python --version
pip list | grep -E "customtkinter|plyer|pystray"
```

## 架构

### 数据流（单向）

```
用户操作 → StateManager.dispatch()
         → TimerState 更新
         → StateManager._notify() 通知所有订阅者
         → UI 组件根据新状态渲染
```

### 核心模块

| 文件 | 职责 |
|------|------|
| `main.py` | 入口：初始化所有模块、生成资源、启动主循环 |
| `config.py` | 所有常量：时长、颜色、字体、中文字符串 |
| `state_manager.py` | **核心**：`TimerState` 不可变数据类 + `StateManager` 单例（观察者模式） |
| `timer_engine.py` | 倒计时引擎：基于 `time.time()` 时间戳（非 `after()` 计数），避免计时漂移 |

### UI 组件（`ui/`）

| 文件 | 组件 |
|------|------|
| `main_window.py` | `MainWindow(CTk)` — 主窗口，组装所有子组件 |
| `progress_ring.py` | `ProgressRing(CTkFrame)` — Canvas 圆环倒计时 |
| `controls.py` | `ControlPanel(CTkFrame)` — 开始/暂停/重置/跳过按钮 |
| `session_counter.py` | `SessionCounter(CTkFrame)` — 今日番茄计数 |
| `settings_panel.py` | `SettingsPanel(CTkFrame)` — 置顶/声音开关 |

### 服务层（`services/`）

| 文件 | 职责 | 依赖 |
|------|------|------|
| `notification.py` | 桌面通知 | `plyer` |
| `sound.py` | 提示音播放 | `winsound`（标准库） |
| `tray.py` | 系统托盘图标和菜单 | `pystray`, `Pillow` |

### 状态机

```
IDLE ──[start]──> WORK ──[timeout, sessions<4]──> SHORT_BREAK ──[timeout]──> WORK
                     │                                     │
                     └──[timeout, sessions=4]──> LONG_BREAK ──[timeout]──> WORK (sessions 重置)
                     │
                     └──[pause]──> PAUSED ──[start]──> 恢复
```

### 状态对象（`TimerState`）

不可变 dataclass：`phase`, `remaining_seconds`, `total_seconds`, `sessions_completed`, `is_running`, `always_on_top`, `sound_enabled`

### 计时精度策略

存储 `start_time` 时间戳，每次 tick 用 `total - (now - start_time)` 计算剩余时间，不依赖 `tk.after()` 的累积计数，避免漂移。

### 持久化

每日番茄完成数存 JSON 到 `%APPDATA%/pomodoro_timer/sessions.json`，格式 `{"date": "2026-06-11", "count": 3}`。

## 关键设计决策

- **tkinter Canvas 自绘圆环**而非图片资源，颜色可随阶段动态切换
- **pystray 在守护线程运行**，tkinter 在主线程运行，两者通过 `window.after()` 通信
- **关闭窗口 = 最小化到托盘**，真正退出需通过托盘右键菜单
- **首次运行时自动生成** 图标（ICO）和提示音（WAV），无需手动准备资源文件
