# sources/test-tools/syzkaller/pkg/manager/testdata/2

Purpose: Crash-report fixture for HID/USB subsystem extraction.

Important content: The report contains a general protection fault in `logi_dj_probe` at `drivers/hid/hid-logitech-dj.c:1910`, with a stack through HID and USB probe paths (`drivers/hid`, `drivers/hid/usbhid`, `drivers/usb/core`). It includes a disassembly block and tail-report separator.

Control flow and state: `TestGetSubsystems` saves the fixture and expects subsystem names `input` and `usb` based on configured path rules.

Dependencies and integration: Exercises Linux report guilty-file parsing, path-rule matching with overlapping include rules, and multi-subsystem output.

Risks: The stack contains both HID and USB paths; path-rule ordering and deduplication must preserve the expected two subsystems. Report parser changes could choose a different guilty frame.

Test signals: Positive fixture for multi-subsystem classification from a realistic probe crash.
