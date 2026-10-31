#!/usr/bin/env python3
"""Android bug evidence collector. One command grabs everything a bug report
needs from the connected device: device info, screenshot, and crash logs.

Usage:
  python collect_evidence.py [--package com.example.app] [--out evidence]

Creates evidence/<n>/ with: device_info.txt, screenshot.png, logcat_errors.txt,
crashes.txt (parsed FATAL EXCEPTION blocks) and prints a summary to paste into a bug report.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def adb(*args, binary=False):
    r = subprocess.run(["adb", *args], capture_output=True, timeout=60)
    if binary:
        return r.stdout
    return r.stdout.decode("utf-8", "replace").strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--package", default=None, help="app package to filter logs for")
    p.add_argument("--out", default="evidence")
    a = p.parse_args()

    try:
        devices = adb("devices")
    except FileNotFoundError:
        print("ERROR: adb not found in PATH. Install Android Platform Tools.")
        return 1
    lines = [l for l in devices.splitlines()[1:] if l.strip()]
    attached = [l.split()[0] for l in lines if l.strip().endswith("device")]
    if not attached:
        print("ERROR: no device connected. Check: USB cable, USB debugging enabled, "
              "or start an emulator. `adb devices` output:")
        print(devices)
        return 1
    if len(attached) > 1:
        print(f"NOTE: {len(attached)} devices attached, using first: {attached[0]}")

    base = Path(a.out)
    base.mkdir(parents=True, exist_ok=True)
    n = 1
    while (base / f"{n:03d}").exists():
        n += 1
    out = base / f"{n:03d}"
    out.mkdir()

    model = adb("shell", "getprop", "ro.product.model")
    android = adb("shell", "getprop", "ro.build.version.release")
    sdk = adb("shell", "getprop", "ro.build.version.sdk")
    build = adb("shell", "getprop", "ro.build.display.id")
    info = (f"Device model: {model}\nAndroid version: {android} (SDK {sdk})\n"
            f"Build: {build}\n")
    if a.package:
        ver = adb("shell", "dumpsys", "package", a.package)
        m = re.search(r"versionName=(\S+)", ver)
        info += f"App package: {a.package}\nApp version: {m.group(1) if m else 'NOT INSTALLED?'}\n"
    (out / "device_info.txt").write_text(info, encoding="utf-8")

    png = adb("exec-out", "screencap", "-p", binary=True)
    shot = ""
    if png[:8] == b"\x89PNG\r\n\x1a\n":
        (out / "screenshot.png").write_bytes(png)
        shot = str(out / "screenshot.png")
    else:
        shot = "(screenshot failed — screen may be locked or protected)"

    log = adb("logcat", "-d", "-v", "time", "*:E")
    if a.package:
        keep = [l for l in log.splitlines() if a.package in l or "FATAL" in l or "AndroidRuntime" in l]
        log_filtered = "\n".join(keep)
    else:
        log_filtered = log
    (out / "logcat_errors.txt").write_text(log_filtered, encoding="utf-8")

    crashes = re.findall(r"(FATAL EXCEPTION.*?)(?=\n\S|\Z)", log, re.S)
    crash_summary = ""
    if crashes:
        (out / "crashes.txt").write_text("\n\n====\n\n".join(crashes), encoding="utf-8")
        first_lines = [c.splitlines()[0:3] for c in crashes]
        crash_summary = f"{len(crashes)} crash(es) found! First: " + " | ".join(first_lines[-1])
    else:
        crash_summary = "no FATAL crashes in current log buffer"

    print(f"OK: evidence saved to {out}\\")
    print("--- paste into bug report Environment section ---")
    print(info.strip())
    print("--------------------------------------------------")
    print(f"Screenshot: {shot}")
    print(f"Crashes: {crash_summary}")
    print(f"Error log lines: {len(log_filtered.splitlines())} (see logcat_errors.txt)")
    print("\nNEXT STEP FOR AI: Read the screenshot.png to see the screen state, and read "
          "crashes.txt (if any) to extract the exception for the bug report.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
