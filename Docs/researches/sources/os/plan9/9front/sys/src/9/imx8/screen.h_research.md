# File Research: sources/os/plan9/9front/sys/src/9/imx8/screen.h

Role: Shared display/mouse/draw declarations for the i.MX8 screen stack.

Key contents:
- Declares mouse state/control hooks from `devmouse.c`.
- Declares screen functions: initialization, blanking, flushing, attach, cursor control, cursor loading, mouse control/resizing/redraw.
- Declares global `drawlock`.
- Defines `ishwimage(i)` as always true for `devdraw.c`.
- Declares software cursor helper functions.

Dependencies:
- Included by `lcd.c` and `screen.c`, and used with Plan 9 draw/devdraw code.

Notes:
- `screeninit` parameter name is misspelled `hight` in the prototype but implementation uses `height`.
