# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.h

## Role
Header for the custom Win32 text-window class used by Ghostscript GUI launcher.

## Contents
- Defines `TW`, holding title/icon, screen buffer, screen size, drag/drop strings, window handle, keyboard buffer, quit state, line input buffer/state, focus/input state, font settings, caret/cursor metrics, scroll state, and saved geometry.
- Declares text window lifecycle, input, output, scrolling, class registration, window creation, font/size/position, drag/drop, and handle accessor functions.

## Important Interfaces
- `TW` struct.
- `text_new`, `text_destroy`, `text_kbhit`, `text_gets`, `text_read_line`, `text_putch`, `text_write_buf`, `text_puts`, `text_to_cursor`, `text_register_class`, `text_create`, `text_font`, `text_size`, `text_setpos`, `text_getpos`, `text_drag`, `text_get_handle`.

## Dependencies And Coupling
- Requires Win32 types (`HICON`, `BYTE`, `POINT`, `HWND`, `BOOL`, `HFONT`).
- Used by `dwmain.c` and implemented by `dwtext.c`.

## Risks And Notes
- Declares `int getch(void);` rather than `text_getch`, even though implementation defines `text_getch`; this may be a stale declaration.
- `TW` is fully exposed, so callers can couple to internal state.

## Filesystem Relevance
None directly.
