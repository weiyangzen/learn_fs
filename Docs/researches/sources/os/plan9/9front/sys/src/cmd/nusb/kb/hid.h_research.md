# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/kb/hid.h

This header defines HID constants for the keyboard/mouse driver. It contains stack size, max simultaneous keys, class/subclass/protocol identifiers for boot mouse, generic HID, non-boot pointer, and boot keyboard endpoints, HID class request codes, boot/report protocol values, output-report selector, report descriptor item tags, and main-item flag bits.

These constants drive descriptor selection, `SET_IDLE`/`SET_PROTOCOL`/`SET_REPORT` control transfers, and the generic HID report parser in `kb.c`. The item tags and flags are parallel to the joystick header but include keyboard/mouse-specific CSP values.
