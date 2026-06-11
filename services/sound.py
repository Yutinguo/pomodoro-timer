"""声音播放 — 使用 winsound（Windows 内置）"""

import os
import winsound


# 提示音文件路径
ALERT_WAV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               "assets", "alert.wav")


def play_alert():
    """播放提示音。优先使用自定义 WAV 文件，否则使用系统提示音。"""
    try:
        if os.path.exists(ALERT_WAV_PATH):
            winsound.PlaySound(ALERT_WAV_PATH,
                               winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            # 系统默认提示音（非阻塞）
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        # 静默失败，不影响主流程
        pass
