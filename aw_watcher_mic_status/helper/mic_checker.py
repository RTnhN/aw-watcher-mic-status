from __future__ import annotations

import glob
import platform
import subprocess
import sys
from typing import Callable


def is_mic_active() -> tuple[bool, str]:
    """Return microphone activity status for the current OS."""
    return _dispatch(
        windows=_win_mic_active,
        darwin=_mac_mic_active,
        linux=_nix_mic_active,
    )


def _dispatch(**impl: Callable[[], tuple[bool, str]]) -> tuple[bool, str]:
    osname = platform.system().lower()
    if osname.startswith("win"):
        return impl["windows"]()
    if osname == "darwin":
        return impl["darwin"]()
    if osname == "linux":
        return impl["linux"]()
    return (False, "Not supported")


def _safe_run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run *cmd*; never raise use returncode & output instead."""
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )


if sys.platform.startswith("win"):
    import winreg

    _REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"

    def _win_cap_active(cap: str) -> tuple[bool, str]:
        """
        Check CapabilityAccessManager usage counters.
        A value `LastUsedTimeStart` > `LastUsedTimeStop`
        means the capability is in use *right now*.
        """
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, rf"{_REG_PATH}\{cap}"
            ) as root:
                for idx in range(winreg.QueryInfoKey(root)[0]):
                    sub = winreg.EnumKey(root, idx)
                    with winreg.OpenKey(root, sub) as key:
                        if _subkeys_active(key):
                            return (True, sub)
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, rf"{_REG_PATH}\{cap}\NonPackaged"
            ) as root:
                # packaged & non-packaged subkeys live one level deeper
                for idx in range(winreg.QueryInfoKey(root)[0]):
                    sub = winreg.EnumKey(root, idx)
                    with winreg.OpenKey(root, sub) as key:
                        if _subkeys_active(key):
                            return (True, sub)

        except OSError as e:
            print(f"winreg error: {e}")

        return (False, "off")

    def _subkeys_active(hkey) -> bool:
        try:
            start, _ = winreg.QueryValueEx(hkey, "LastUsedTimeStart")
            stop, _ = winreg.QueryValueEx(hkey, "LastUsedTimeStop")
            # both are Windows FILETIME (100-ns since 1601-01-01); 0 means never
            return start > stop
        except FileNotFoundError:
            return False

    def _win_mic_active() -> tuple[bool, str]:
        return _win_cap_active("microphone")


def _mac_mic_active() -> tuple[bool, str]:
    """
    Quick heuristic: list open CoreAudio capture streams.
    We call `lsof -Fn -c coreaudiod` (no sudo needed);
    presence of any /dev/audio or /dev/*input* node implies use.
    """
    out = _safe_run(["lsof", "-Fn", "-c", "coreaudiod"])
    if out.returncode:
        return (False, "off")
    if any("/dev/" in line for line in out.stdout.splitlines()):
        return (True, "Active")
    return (False, "off")


def _nix_mic_active() -> tuple[bool, str]:
    """
    ALSA exposes stream state under
    /proc/asound/card*/pcm*/sub0/status.
    A line 'state: RUNNING' denotes capture in progress.
    """
    for status_file in glob.glob("/proc/asound/card*/pcm*/sub0/status"):
        try:
            with open(status_file) as fh:
                if "state: RUNNING" in fh.read():
                    return (True, "Active")
        except FileNotFoundError:
            continue
    return (False, "off")


# ----------------------------  self-test  ---------------------------- #
if __name__ == "__main__":
    print("mic    :", is_mic_active())
