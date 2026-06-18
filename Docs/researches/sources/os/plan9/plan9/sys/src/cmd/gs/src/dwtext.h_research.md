# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.h

Purpose: Declares the Win32 text-window data structure and API.

Key structure:
- `TW` stores title/icon, screen buffer and dimensions, drag strings, window handle, keyboard circular buffer, line buffer, focus/caret state, font settings, character metrics, cursor/client/scroll positions, and saved window rectangle.

Public API:
- Create/destroy: `text_new`, `text_destroy`.
- Input: `text_kbhit`, `text_gets`, `text_read_line`.
- Output: `text_putch`, `text_write_buf`, `text_puts`.
- Window/cursor: `text_to_cursor`, `text_register_class`, `text_create`, `text_get_handle`.
- Configuration: `text_font`, `text_size`, `text_setpos`, `text_getpos`, `text_drag`.

Notes:
- Declares `int getch(void);` even though the implementation provides `text_getch(TW *)`; this may be legacy or stale.
- Requires Win32 types.

Filesystem relevance: None.
