---
name: mobile-test
description: Test mobile apps (Android/iOS) — drive a real Android device or emulator via adb, install builds, capture screenshots and logs, generate mobile-specific test cases and checklists. Use when the user is testing a mobile app, APK, Android or iOS application.
---

# Mobile App Tester

Help the tester test mobile applications. Note: this machine is Windows — Android testing works fully; iOS automation needs a Mac, so for iOS focus on test design, checklists, and analyzing logs/screenshots the tester provides.

## Mode 1: Hands-on Android testing (adb)

First check the setup: run `adb devices`. If adb is missing, guide the user to install Android Platform Tools and enable USB debugging on the device (Settings → Developer options).

**When the user reports a bug or crash, ALWAYS run the evidence collector FIRST** — one command grabs device info, a screenshot, error logs, and parses crash stack traces:

```
python .claude/skills/mobile-test/scripts/collect_evidence.py --package <app.package.name>
```

It saves everything to `evidence/<n>/` and prints an Environment block ready for the bug report. Then: Read the `screenshot.png` to see the screen state, read `crashes.txt` if it found crashes, and write the bug report (bug-report skill format) including the stack trace's first lines translated to plain language.

Useful actions you can do for the tester:
- **Install a build:** `adb install -r app.apk`
- **Screenshot:** `adb exec-out screencap -p > screen.png` (then Read the image to analyze it)
- **Screen recording:** `adb shell screenrecord /sdcard/test.mp4` (max 3 min), then `adb pull`
- **Crash logs:** `adb logcat -d *:E` or `adb logcat -d | grep -i "FATAL\|<package name>"` — always grab logcat right after a crash and translate the stack trace into plain language for the bug report
- **Device info for bug reports:** `adb shell getprop ro.build.version.release` (Android version), `ro.product.model` (device model)
- **Simulate conditions:** airplane mode `adb shell cmd connectivity airplane-mode enable`, kill app `adb shell am force-stop <package>`, revoke a permission `adb shell pm revoke <package> <permission>`, change font scale/display size for accessibility checks
- **Deep links:** `adb shell am start -a android.intent.action.VIEW -d "<url>"`

When the tester reports "the app crashed", automatically: pull logcat, find the exception, and produce a ready bug report (use the bug-report skill format) including device model, OS version, and the stack trace.

## Mode 2: Mobile test case design

When generating test cases for mobile, ALWAYS add these mobile-specific categories on top of normal functional cases:

- **Interruptions:** incoming call/SMS during a flow, notification tap, app switch and return, screen lock/unlock mid-operation
- **Lifecycle:** kill app and reopen (state restored?), background for a long time, low memory kill, update app with old data installed
- **Network:** offline mode, switch Wi-Fi ↔ mobile data mid-request, slow/flaky network, request timeout behavior
- **Permissions:** deny each permission, revoke while app is running, "don't ask again" state
- **Device variety:** small screen, tablet, different OS versions (check the app's minSdk), dark mode, large font size (accessibility), RTL language (Arabic!)
- **Orientation:** rotate on every screen, especially during input or loading
- **Battery/performance:** battery saver mode, app size, startup time, jank on old devices
- **Platform rules:** back button behavior (Android), swipe gestures (iOS), safe areas/notch

## Mode 3: Mobile automation

- Recommend **Maestro** for a tester starting automation — YAML flows, very simple, works on Android + iOS. Write flows like:
  ```yaml
  appId: com.example.app
  ---
  - launchApp
  - tapOn: "Login"
  - inputText: "user@test.com"
  ```
- Recommend **Appium** when the team needs a full framework integrated with their existing language (Java/Python/JS).
- Same quality rules as the automate skill: no fixed sleeps, independent tests, meaningful assertions.

## Safety

- Never wipe a device (`adb shell pm clear`, factory reset) without explicit confirmation — it deletes app data.
- Only test apps the tester's company owns or has permission to test.
