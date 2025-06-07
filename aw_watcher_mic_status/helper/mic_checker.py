from __future__ import annotations

import glob
import platform
import subprocess
import sys
from typing import Callable, Optional

def is_mic_active() -> Optional[bool]:
    """Return microphone activity status for the current OS."""
    return _dispatch(
        windows=_win_mic_active,
        darwin=_mac_mic_active,
        linux=_nix_mic_active,
    )

def _dispatch(**impl: Callable[[], Optional[bool]]) -> Optional[bool]:
    osname = platform.system().lower()
    if osname.startswith("win"):
        return impl["windows"]()
    if osname == "darwin":
        return impl["darwin"]()
    if osname == "linux":
        return impl["linux"]()
    return None  # unsupported platform


def _safe_run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run *cmd*; never raise use returncode & output instead."""
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

if sys.platform.startswith("win"):
    import ctypes
    import winreg

    _REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"

    def _win_cap_active(cap: str) -> Optional[bool]:
        """
        Check CapabilityAccessManager usage counters.
        A value `LastUsedTimeStart` > `LastUsedTimeStop`
        means the capability is in use *right now*.
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf"{_REG_PATH}\{cap}") as root:
                if _subkeys_active(root):
                    return True
                # packaged & non-packaged subkeys live one level deeper
                for idx in range(winreg.QueryInfoKey(root)[0]):
                    sub = winreg.EnumKey(root, idx)
                    with winreg.OpenKey(root, sub) as key:
                        if _subkeys_active(key):
                            return True
        except OSError:
            pass
        return False

    def _subkeys_active(hkey) -> bool:
        try:
            start, _ = winreg.QueryValueEx(hkey, "LastUsedTimeStart")
            stop, _ = winreg.QueryValueEx(hkey, "LastUsedTimeStop")
            # both are Windows FILETIME (100-ns since 1601-01-01); 0 means never
            return start > stop
        except FileNotFoundError:
            return False

    def _win_mic_active() -> Optional[bool]:
        return _win_cap_active("microphone")


def _mac_mic_active() -> Optional[bool]:
    """
    Quick heuristic: list open CoreAudio capture streams.
    We call `lsof -Fn -c coreaudiod` (no sudo needed);
    presence of any /dev/audio or /dev/*input* node implies use.
    """
    out = _safe_run(["lsof", "-Fn", "-c", "coreaudiod"])
    if out.returncode:
        return None
    return any("/dev/" in line for line in out.stdout.splitlines())

def _nix_mic_active() -> Optional[bool]:
    """
    ALSA exposes stream state under
    /proc/asound/card*/pcm*/sub0/status.
    A line 'state: RUNNING' denotes capture in progress.
    """
    for status_file in glob.glob("/proc/asound/card*/pcm*/sub0/status"):
        try:
            with open(status_file) as fh:
                if "state: RUNNING" in fh.read():
                    return True
        except FileNotFoundError:
            continue
    return False


# ----------------------------  self-test  ---------------------------- #
if __name__ == "__main__":
    print("mic    :", is_mic_active())
