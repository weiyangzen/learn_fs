# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/kb.c

USB HID keyboard and mouse driver.

Major responsibilities:
- Opens interrupt-in endpoints for boot keyboards and boot/report-protocol pointers.
- Writes keyboard scan codes to `#I/kbin` and mouse events to `#m/mousein`, with shared `Kin` reference management.
- Maps HID keyboard keycodes through `sctab[]` into Plan 9 scan codes.
- Handles keyboard modifier diffs, key down/up synthesis, and key repeat via a separate repeat process.
- Handles pointer reports in either boot protocol (`ptrbootpvals`) or parsed HID report form (`ptrrepvals`).
- Applies optional pointer acceleration and formats mouse events as `m%11d %11d %11d`.
- Configures HID devices using first configuration/report descriptor when possible, falling back to boot protocol.
- Includes recovery logic for babble/read errors by asking the USB endpoint/device to reset and reopening data.

Important paths:
- `kbmain` decides whether keyboard and/or pointer endpoints are enabled, allocates `KDev`, and starts `kbdwork` or `ptrwork`.
- `kbstart` opens the endpoint, sets idle/report/boot protocol, opens data, and creates the worker.
- `kbfatal` detaches and closes the USB device on terminal errors.

Quirks:
- Report descriptor parsing is only pointer-oriented.
- Some debug scan codes mutate driver debug level.
- Comments note incomplete recovery semantics for bundled devices.
