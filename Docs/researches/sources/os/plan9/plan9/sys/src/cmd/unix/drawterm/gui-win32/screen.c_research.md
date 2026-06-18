# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/screen.c

Win32 GDI screen, input, cursor, and clipboard backend for drawterm.

Key responsibilities:
- Detects desktop bit depth, chooses a compatible Plan 9 image channel, allocates a full-desktop `Memimage`, and starts a `winscreen` kernel process.
- Registers a Win32 window class and creates the drawterm screen window.
- Implements `screenload()` using `StretchDIBits()` from the backing `Memimage` into the window DC.
- Handles mouse, wheel, paint, keyboard, palette, close, and cursor messages in `WindowProc`.
- Maps selected virtual keys to Plan 9 private keyboard constants and sends `WM_CHAR` text to `kbdq`.
- Builds a Plan 9-compatible 8-bit palette and BITMAPINFO table.
- Implements Win32 cursor creation from Plan 9 cursor bitmaps.
- Implements clipboard read/write for `CF_UNICODETEXT` and `CF_TEXT`.
- Provides `atlocalconsole()` returning true.

Important behavior:
- Uses desktop dimensions for the backing screen rectangle, even though the window starts with default Win32 sizing.
- Clips flush rectangles both to the backing image and current window rectangle.
- Right mouse with Shift is mapped as button 2; otherwise right mouse maps as button 3.
- Mouse wheel emits Plan 9 buttons 8 or 16.
- Unicode clipboard writes also publish a plain `CF_TEXT` copy.

Dependencies:
- Depends on Win32 windowing/GDI/clipboard APIs plus drawterm kernel mouse/keyboard queues.
- Uses `wstrutflen()` and `wstrtoutf()` for Unicode clipboard reads.

Notable risks:
- `WM_MOUSEWHEEL` sets `b` before `b` is initialized and then falls through into code that resets `b`, so wheel-button behavior appears suspect.
- `WM_CHAR` maps `'\n'` to `'\r'` and `'\r'` to `'\n'`, which is intentional but host-message dependent.
- `setcolor()` is a no-op, so palette mutation requests are ignored.
- The backing image is not resized with the window.
