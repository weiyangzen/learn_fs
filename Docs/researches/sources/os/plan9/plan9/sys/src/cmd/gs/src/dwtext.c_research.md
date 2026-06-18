# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtext.c

Purpose: Win32 text-window/terminal abstraction used by the Ghostscript GUI launcher.

Major responsibilities:
- Creates a fixed-size character grid window backed by `ScreenBuffer`.
- Renders text with a selectable monospaced font.
- Maintains scroll bars and cursor visibility.
- Provides keyboard input buffering, line input, and basic editing.
- Supports clipboard copy/paste and drag/drop file injection.
- Handles caret/focus and window message processing.

Key API implementations:
- Lifecycle: `text_new`, `text_destroy`, `text_register_class`, `text_create`.
- Configuration: `text_size`, `text_font`, `text_drag`, `text_setpos`, `text_getpos`, `text_get_handle`.
- Output: `text_putch`, `text_write_buf`, `text_puts`.
- Input: `text_kbhit`, `text_getch`, `text_read_line`, `text_gets`.
- UI internals: `WndTextProc`, `text_copy_to_clipboard`, `text_paste_from_clipboard`, `text_drag_drop`.

Notable behavior:
- `text_read_line` returns non-NUL-terminated chunks for Ghostscript stdio compatibility.
- Drag/drop injects configured prefix, normalized filename with `/`, and suffix into the keyboard buffer.
- Clipboard copy exports trimmed screen-buffer lines.
- `WM_CLOSE` marks `quitnow` and changes title to “closing” but defers actual destruction until Ghostscript exits.

Risks/legacy notes:
- Uses `SetWindowLong`/`GetWindowLong` pointer casts, not 64-bit safe.
- `text_write_buf` uses bitwise `&` in a loop condition where `&&` was likely intended.
- Fixed-size input line buffer is 256 bytes.
- The opening comment appears malformed: the descriptive block starts `/* Microsoft Windows text window for Ghostscript.` and source continues with includes; compilers may tolerate only if the actual file text is historically intended, but as read it looks like an unterminated comment before includes.

Filesystem relevance: None directly. Drag/drop only converts dropped file paths into Ghostscript commands.
