# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/devmouse.c

Synthetic mouse and cursor device for the VNC environment.

Key responsibilities:
- Provides `/dev/mouse` and `/dev/cursor`.
- Tracks current mouse position, buttons, event counter, timestamp, and a ring buffer of button-change events.
- Enforces a single open reader for `/dev/mouse`.
- Reads mouse events in Plan 9 `m%11d...` text format.
- Reads and writes cursor bitmaps in Plan 9 cursor format.
- Supports mouse warping by writing coordinates to `/dev/mouse`.
- Maintains button remapping infrastructure and cursor redraw scheduling.

Important behavior:
- Button change events are queued; motion-only reads return current state when no queued event exists.
- If the button queue fills, queued events are dropped until the reader catches up.
- Last close resets the cursor to the arrow.
- Cursor updates call `setcursor()`, `cursoroff()`, `cursoron()`, and `mouseclock()`.

Risks:
- `setbuttonmap()` exists but is not wired into exposed control parsing here.
- Mouse reader concurrency assumes only one active reader.
