from typing import Callable, Optional

from pynput import keyboard
from qtpy import QtCore


class Hotkey(QtCore.QObject):
    pressed = QtCore.Signal()

    def __init__(self, hotkey):
        super().__init__()
        self.hotkey = hotkey

    def emit_signal(self, *args):
        print(f"emit for {self.hotkey}")
        self.pressed.emit()

    def start(self, handler=None):
        manager = HotkeyManager.get_instance()
        manager.add(self.hotkey, self.emit_signal)
        if handler:
            self.pressed.connect(handler)
        manager.restart()

    def stop(self, disconnect=True, restart_manager=True):
        if disconnect:
            self.pressed.disconnect()
        manager = HotkeyManager.get_instance()
        manager.remove(self.hotkey)
        if restart_manager:
            manager.restart()

    def set_hotkey(self, hotkey):
        if self.hotkey == hotkey:
            return

        self.stop(disconnect=False, restart_manager=False)
        self.start()


class HotkeyManager:
    instance: Optional["HotkeyManager"] = None

    def __init__(self) -> None:
        self.hotkeys = {}
        self.changed = False
        self.listener = None

    @classmethod
    def get_instance(cls) -> "HotkeyManager":
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def add(self, hotkey: str, func: Callable[[], None]):
        self.hotkeys[hotkey] = func
        self.changed = True

    def remove(self, hotkey: str):
        del self.hotkeys[hotkey]
        self.changed = True

    def running(self) -> bool:
        return self.listener is not None

    def start(self):
        self.listener = keyboard.GlobalHotKeys(self.hotkeys)
        self.listener.start()

    def stop(self):
        if self.listener is not None:
            self.listener.stop()
        self.listener = None

    def restart(self, start_if_stopped: bool = False):
        if self.running() or start_if_stopped:
            self.stop()
            self.start()
