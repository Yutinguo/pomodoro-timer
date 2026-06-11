"""桌面通知 — 使用 plyer 跨平台通知 API"""

from plyer import notification


def send_notification(title: str, message: str):
    """发送桌面通知"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="番茄钟",
            timeout=5,
        )
    except Exception:
        # 通知失败不阻塞主流程
        pass
