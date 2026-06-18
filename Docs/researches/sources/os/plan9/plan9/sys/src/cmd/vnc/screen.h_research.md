# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.h

Shared screen, cursor, draw-lock, and framebuffer declarations for VNC device code.

Key contents:
- Defines `Cursorinfo` as a `Cursor` plus lock.
- Declares global cursor state, arrow cursor, framebuffer image, cursor version, and cursor position.
- Declares mouse, cursor, framebuffer flush, draw lock, colormap, screen blanking, screen initialization, mouse tracking, and `attachscreen()` functions.
- Defines `TK2SEC(x)` as `0`.
- Declares `fsinit()`.

Role:
- Connects `screen.c`, `devdraw.c`, `devmouse.c`, and related VNC server code.

Risks:
- `TK2SEC` is a stub, so code depending on real tick conversion would not get useful timing.
