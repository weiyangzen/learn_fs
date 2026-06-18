# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/devmouse.c

## Role

`devmouse.c` implements a minimal `/dev/mouse`, `/dev/cursor`, `/dev/mousein`, and `/dev/mousectl` device for the VNC server's private desktop.

## Device Behavior

- Maintains global `Mouseinfo mouse` and `Cursorinfo cursor`.
- Exposes a default arrow cursor and supports writing cursor image data to `/dev/cursor`.
- Allows only one open reader for `/dev/mouse`.
- `mouseread()` blocks with `rendsleep()` until movement, button, or resize state changes, then returns Plan 9 mouse event records.
- `mousewrite()` on `/dev/mouse` parses warp coordinates and calls `absmousetrack()` and `mousewarpnote()`.
- `absmousetrack()` clamps coordinates to `gscreen->clipr`, updates state, queues button transitions, wakes mouse readers, and turns the cursor on.
- `mouseresize()` marks a resize event and wakes readers.

## Notable Limitations And Risk Areas

- `mousein` and `mousectl` are present but intentionally raise placeholder errors on open.
- Button-transition queue overflow drops extra transition events until a reader drains the queue.
- Cursor updates directly affect the global screen cursor and rely on `screen.c` drawing logic.
- Mouse tracking is ignored before `gscreen` exists.
