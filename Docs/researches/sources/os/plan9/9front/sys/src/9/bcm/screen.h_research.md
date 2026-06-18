# File Research: sources/os/plan9/9front/sys/src/9/bcm/screen.h

Screen, cursor, and mouse interface declarations for BCM display code.

Key contents:
- Declares mouse tracking, mouse acceleration, and mouse byte-input helpers.
- Declares screen blanking, framebuffer flush, `attachscreen()`, cursor on/off/load, and resize/redraw hooks.
- Defines `ishwimage(i)` as always true for `devdraw`.
- Declares software cursor functions.

Role:
- Shared interface between architecture screen code, draw device code, and mouse/cursor implementations.
