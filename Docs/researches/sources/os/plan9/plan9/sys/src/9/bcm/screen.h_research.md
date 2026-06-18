# File Research: sources/os/plan9/plan9/sys/src/9/bcm/screen.h

Screen/mouse interface declarations for the BCM graphics path.

Key contents:
- Defines `Cursorinfo` as `Cursor` plus `Lock`.
- Declares mouse functions, cursor globals, screen functions, and `drawlock`.
- Provides `ishwimage(i) 1` for `../port/devdraw.c`.

This header links `screen.c`, reused mouse code, and shared draw-device code.
