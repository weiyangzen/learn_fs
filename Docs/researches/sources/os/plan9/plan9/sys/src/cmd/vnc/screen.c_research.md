# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.c

In-memory framebuffer, cursor, and text console backing for the VNC environment.

Key responsibilities:
- Initializes a `Memimage` screen with requested dimensions and channel.
- Creates cursor mask images and default arrow cursor state.
- Draws an initial Plan 9 console window using the default memory font.
- Implements `attachscreen()` for `devdraw.c`.
- Provides stub color map operations and blanking hook.
- Converts Plan 9 cursor bitmaps into memory images and draws cursor overlays.
- Tracks cursor position, offscreen hiding, and cursor version.
- Implements console text output with newline, carriage return, tab, backspace, wrapping, scrolling, and dirty rectangle flushing.

Important behavior:
- `screenputs()` locks draw state while rendering UTF-8 runes.
- Console scroll moves the window contents up by eight font heights.
- Cursor “on” updates cursor position from `mousexy()`; cursor “off” moves it offscreen.

Risks:
- `getcolor()`/`setcolor()` are stubs, so colormap behavior is limited.
- `flushmemscreen()` is external and central to VNC update propagation.
