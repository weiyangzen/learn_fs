# File Research: sources/os/plan9/9front/sys/src/9/port/devmouse.c

Purpose: Implements the `#m` mouse device, exposing `cursor`, `mouse`, `mousein`, and `mousectl` for cursor shape, event reads, injected input, and control.

Key logic:
- Maintains global `Mouseinfo` state with current position/buttons, read counters, resize state, a button-change event ring, and redraw rendezvous.
- `mouseinit` installs the default arrow cursor and starts a redraw kernel process when a monitor exists.
- `mouseread` returns binary cursor data, formatted mouse events (`m`/`r` records), or injected-current state from `mousein`.
- `mousewrite` accepts cursor updates, absolute/scaled/relative injected events, absolute moves through `mouse`, and `mousectl` commands.
- `mousectl` supports button-map changes, button swapping, scroll swapping, screen blanking, blank timeout, and driver-specific wildcard controls.
- `mousetrack`, `absmousetrack`, and `scmousetrack` update state, clamp to screen bounds, queue button events, wake readers, and schedule redraw.
- Serial protocol helpers parse Microsoft 3-byte, IntelliMouse 4-byte wheel, and Logitech 5-byte mouse byte streams.

Dependencies and integration:
- Uses draw/screen globals (`gscreen`, `drawlock`, `cursoroff/on`, `setcursor`, `blankscreen`), queues for serial input callbacks, and Plan 9 device helpers.

Risks and notes:
- `/dev/mouse` is single-open; `/dev/mousein` is eve-only and has per-open injected button state.
- Button and scroll remapping affects only the user-visible event encoding, not raw internal button state.
- Screen blanking is tied to mouse inactivity and read wakeups.
