# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/cons.h

This header is the shared interface for the Plan 9 terminal emulator.

Console control:
- Defines `Consstate` with `raw` and `hold`.
- Declares `consctl()` and global `cs`, used to emulate `/dev/consctl` state.

Screen constants:
- Margins/insets, buffer sizes, history size, and state constants for canonical input and scrolling.

Text attributes:
- Bit flags for high intensity, underline, blink, reverse, and invisible text.

Input helpers:
- `button2()` and `button3()` macros interpret Plan 9 mouse button state.
- `ttystate` maps raw/cooked modes to CR/NL translation settings.

Function key model:
- `struct funckey` maps names to escape sequences.
- Declares key tables for VT100, VT220, ANSI, and xterm.

Shared emulator state:
- Cursor coordinates and limits, scrollback, attributes, terminal name, scroll region, colors, cursor state, and no-color flag.

Shared functions:
- Terminal core: `emulate`, `host_avail`, `get_next_char`.
- Drawing/layout: `clear`, `newline`, `scroll`, `backup`, `pt`, `drawstring`, `curson`, `cursoff`, `setdim`.
- Host I/O: `sendnchars`, `sendnchars2`, `funckey`.
- Parsing utilities: `number`.

Role:
- This file ties together `main.c`, `vt.c`, `hp.c`, `event.c`, and `consctl.c`.
