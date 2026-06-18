# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtext.c

## Role
Custom Win32 text-window implementation used as Ghostscript GUI stdio console.

## Contents
- Defines a `TW`-backed text window class with fixed-size screen buffer, keyboard circular buffer, font metrics, scroll state, drag/drop strings, and line-input buffering.
- Implements font selection, screen size setup, window positioning, object allocation/destruction, class registration, and window creation.
- Writes output into the screen buffer with handling for CR, LF, BEL, tab, backspace/delete, wrapping, and scrolling.
- Provides blocking character and line input using the Windows message loop and keyboard buffer.
- Supports file drag/drop by injecting configured pre/post strings and converted path characters into the keyboard stream.
- Supports copy-to-clipboard of the screen buffer and paste-from-clipboard into the keyboard buffer.
- Window procedure handles system menu copy/paste, focus/caret, move/size/scroll, keyboard navigation, character buffering, painting visible screen buffer lines, drop files, close, and destroy.
- Includes a disabled `NOTUSED` test program.

## Important Interfaces
- `text_new`, `text_destroy`, `text_register_class`, `text_create`.
- `text_font`, `text_size`, `text_setpos`, `text_getpos`.
- `text_putch`, `text_write_buf`, `text_puts`, `text_getch`, `text_gets`, `text_read_line`, `text_kbhit`.
- `text_drag`, `text_to_cursor`, `text_get_handle`.
- Window procedure `WndTextProc`.

## Dependencies And Coupling
- Uses Win32, WindowsX, common dialog, shell drag/drop APIs, and `dwtext.h`.
- Used by `dwmain.c` for GUI Ghostscript stdio.

## Risks And Notes
- The opening file comment is malformed-looking in the read source: `/* Microsoft Windows text window for Ghostscript.` is followed by includes without a visible closing `*/` before them. In this repository content, that would comment out following includes until the later `*/` in an inline include comment; this appears to be an upstream text oddity or transcription artifact worth verifying if compiling.
- Fixed-size buffers, manual circular buffer management, and blocking message loops make behavior sensitive to window lifecycle.
- `text_read_line` does not NUL-terminate returned buffers by design.
- Copy/paste and drag/drop use legacy `CF_TEXT` and fixed path buffers.

## Filesystem Relevance
Only drag/drop filename injection and no direct filesystem implementation.
