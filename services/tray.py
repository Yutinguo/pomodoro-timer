"""系统托盘 — 使用 pystray 创建托盘图标和菜单"""

import threading
from PIL import Image, ImageDraw

import pystray

import config as cfg


def _create_icon_image(size=64):
    """生成番茄图标（红色圆形 + 绿色叶子）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 2
    # 红色圆形（番茄主体）
    draw.ellipse(
        [margin, margin + size // 6, size - margin, size - margin],
        fill="#e0554a",
    )
    # 绿色叶子（顶部小三角）
    leaf_top = (size // 2, margin)
    leaf_left = (size // 3, margin + size // 5)
    leaf_right = (size * 2 // 3, margin + size // 5)
    draw.polygon([leaf_top, leaf_left, leaf_right], fill="#7d9b76")

    return img


class TrayManager:
    """管理系统托盘图标"""

    def __init__(self, window, state_manager):
        self._window = window
        self._sm = state_manager
        self._icon = None
        self._thread = None

    def setup(self):
        """创建并启动托盘图标（在守护线程中运行）"""
        icon_img = _create_icon_image()

        menu = pystray.Menu(
            pystray.MenuItem(
                cfg.STR_TRAY_SHOW,
                self._show_window,
                default=True,
            ),
            pystray.MenuItem(
                cfg.STR_ALWAYS_ON_TOP,
                self._toggle_top,
                checked=lambda item: self._sm.state.always_on_top,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                cfg.STR_TRAY_QUIT,
                self._quit_app,
            ),
        )

        self._icon = pystray.Icon(
            cfg.STR_APP_TITLE,
            icon_img,
            cfg.STR_TOOLTIP,
            menu,
        )

        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def _show_window(self, icon=None, item=None):
        self._window.after(0, self._window.deiconify)
        self._window.after(0, self._window.lift)

    def _toggle_top(self, icon=None, item=None):
        self._window.after(0, self._sm.toggle_always_on_top)

    def _quit_app(self, icon=None, item=None):
        if self._icon:
            self._icon.stop()
        self._window.after(0, self._window.destroy)

    def stop(self):
        """停止托盘图标"""
        if self._icon:
            self._icon.stop()
