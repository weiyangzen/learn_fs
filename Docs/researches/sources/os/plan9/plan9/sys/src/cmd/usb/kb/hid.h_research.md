# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.h

Shared USB HID keyboard/mouse definitions.

Defines:
- HID boot keyboard and pointer CSP constants.
- HID class requests: get protocol, set idle, set protocol.
- Boot/report protocol constants.
- Keyboard modifier bit indexes and masks.
- Plan 9 scan-code constants used by `kb.c`.
- Pointer acceleration and button mask constants.
- `Chain`, a bitstream buffer for HID report parsing.
- `HidInterface` and `HidRepTempl`, the simplified report template used by `hid.c`.
- HID item constants used by the minimal parser.

Exports:
- `kbmain`.
- HID report dump/parse helpers.

This header connects `main.c`, `kb.c`, and `hid.c`.
